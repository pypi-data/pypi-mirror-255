"""MiSoS(oup)"""

import argparse
import glob
import logging
import os
from collections import defaultdict

import yaml
from reframed.solvers.solver import Parameter

from .library.getters import get_biomass, get_exchange_reactions
from .library.minimizer import Minimizer
from .library.readwrite import load_models, read_compounds
from .library.validate import validate_solution_dict
from .reframed.layered_community import LayeredCommunity


def main(args):
    """Main function."""
    logging.info("Loading models.")
    input_paths = glob.glob(args.input[0]) if len(args.input) == 1 else args.input
    models = load_models(input_paths)

    logging.info("Loading media.")
    media = read_compounds(args.media)
    base_medium = media["base_medium"] if "base_medium" in media.keys() else {}

    solutions = defaultdict(dict)

    logging.info("Construct community model.")
    community = LayeredCommunity(
        "community",
        models,
        copy_models=False,
        params={
            Parameter.OPTIMALITY_TOL: args.tolerance,
            Parameter.FEASIBILITY_TOL: args.tolerance,
        },
    )

    for medium_id, medium_composition in media.items():
        if not medium_id == "base_medium" and (
            not args.media_select or medium_id in args.media_select
        ):
            if args.objective:
                logging.info("Set objective function.")
                objective = {reaction: 1 for reaction in args.objective}
            else:
                logging.info("Set objective function to community biomass.")
                objective = {community.merged_model.biomass_reaction: 1}

            logging.info(
                "Compute minimal communities for medium with id: %s", medium_id
            )
            medium = {
                **medium_composition,
                **base_medium,
            }

            minimizer = Minimizer(
                org_id=args.strain,
                medium=medium,
                community=community,
                values=(
                    get_biomass(community)
                    + get_exchange_reactions(community.merged_model)
                ),
                community_size=args.community_size,
                objective=objective,
                parsimony=args.parsimony,
                parsimony_only=args.parsimony_only,
                minimal_growth=args.minimal_growth,
                cache_file=args.cache_file,
            )

            solution = minimizer.minimize()

            solutions[medium_id][args.strain] = solution

    output_dict = {
        k: {org: sol if sol else [{f"Growth_{org}": 0}] for org, sol in v.items()}
        for k, v in solutions.items()
    }

    if args.validate:
        validate_solution_dict(output_dict, args.exchange_format)

    output = yaml.dump(output_dict, Dumper=yaml.CSafeDumper)

    if args.output:
        if not os.path.exists(os.path.dirname(args.output)):
            os.makedirs(os.path.dirname(args.output))
        with open(args.output, "w", encoding="utf8") as file_descriptor:
            file_descriptor.write(output)
    else:
        print(output)


def entry():
    """Misosoup entry point."""
    parser = argparse.ArgumentParser(
        description="""
    Compute minimal supplying communities with MiSoS(oup).

    `misosoup` will create a large community network and evaluate which
    communities can supply growth of some strain (or each other, if no strain
    is chosen).

    It will report the results in `yaml` format, where the dictionaries contain all
    active exchange reactions and their rates, as well as the activity of strains (i.e.
    `y_strain: 1` for any active strain), the community growth rate and the individual
    growth rates of all participating strains:

        ```
        carbon_source:
            strain:
                - {}
                - {}
        ```
    """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input", nargs="+", type=str, help="List or wildcard for model paths."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to output file. Format: YAML. If not supplied, will print to stdout.",
    )
    parser.add_argument(
        "--cache-file",
        type=str,
        help=(
            "Path to cache file. If set, intermediate constraints will be stored and "
            "the run can be restart in case it has been interrupted."
        ),
    )
    parser.add_argument(
        "--media",
        type=str,
        required=True,
        help="Path to media. Format: YAML. File needs to contain dictionary with media, see examples.",
    )
    parser.add_argument(
        "--media-select",
        type=str,
        nargs="+",
        help="List of media names to select which media from the media file to run.",
    )
    parser.add_argument(
        "--strain",
        type=str,
        default="min",
        help="Focal strain model id. If no strain is provided, we compute minimal communities.",
    )
    parser.add_argument(
        "--parsimony", action="store_true", help="Compute parsimony solution."
    )
    parser.add_argument(
        "--parsimony-only",
        action="store_true",
        help="Compute parsimony solution without prior objective optimization.",
    )
    parser.add_argument(
        "--community-size",
        type=int,
        default=0,
        help="Maximum community size. Default: 0 (Arbitrary).",
    )
    parser.add_argument(
        "--minimal-growth",
        type=float,
        default=0.01,
        help=(
            "Minimal required growth for strain or community."
            "Each strain that is considered to grow needs to at least achieve "
            "this minimal growth rate given by this argument."
        ),
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-6,
        help=(
            "Feasibility tolerance during community minimization. "
            "Lower values may lead to slower computations and more communities found."
            "Default: 1e-6."
        ),
    )
    parser.add_argument(
        "--exchange-format",
        type=str,
        default="R_EX_{}_e",
        help=(
            "Regular expression to retrieve the carbon source from an exchange "
            "reaction. The group containing the carbon source, should be named "
            "`carbon_source`; as can be seen from the default. "
            "default: `R_EX_(\\w+)_e"
        ),
    )
    parser.add_argument(
        "--objective",
        type=str,
        nargs="*",
        help=(
            "List of ids that are part of the objective function. By default "
            "the community biomass is maximized."
        ),
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help=(
            "Validate solution. Verify if there are numerical inconsistencies in the "
            "final solution."
        ),
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output.")

    args_parsed = parser.parse_args()

    verbosity = logging.DEBUG if args_parsed.verbose else logging.INFO
    logging.basicConfig(level=verbosity, format="%(asctime)s %(message)s")

    main(args_parsed)
