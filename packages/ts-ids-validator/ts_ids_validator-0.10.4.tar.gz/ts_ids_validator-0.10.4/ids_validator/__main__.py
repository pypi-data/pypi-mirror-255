import argparse
import json
import sys
from pathlib import Path

from ids_validator import tdp_api
from ids_validator.ids_validator import validate_ids, validate_ids_using_tdp_artifact


def main():
    parser = argparse.ArgumentParser(description="Validate IDS Artifacts")

    parser.add_argument(
        "-i",
        "--ids_dir",
        type=Path,
        default=".",
        required=True,
        help="Path to the IDS folder",
    )

    # Add previous IDS artifact dir and TDP-download arguments as mutually exclusive
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-p",
        "--previous_ids_dir",
        type=Path,
        default=None,
        required=False,
        help=(
            "Path to the folder containing the previous version of the IDS, used for "
            "validating breaking changes between versions"
        ),
    )
    download_action = group.add_argument(
        "-d",
        "--download",
        help=(
            "(Boolean flag) Whether to try to download the previous IDS artifact from "
            "TDP. "
            "The namespace, slug and version taken from the provided `--ids_dir` are "
            "used to find the most recent preceding version for the same namespace and "
            "slug (sorted according to SemVer). "
            "This is used to validate changes between IDS versions, see documentation. "
            "To use this option, you must provide API configuration as a JSON config "
            "file (see the `--config` arg), or as the environment variables "
            "'TS_API_URL', 'TS_ORG' and 'TS_AUTH_TOKEN'. "
            "If `--config` is used, then `--download` is required to be set."
        ),
        action="store_true",
        # If a config is passed, the download argument is required
        required=False,
    )
    parser.add_argument(
        "-c",
        "--config",
        help=(
            "Configuration for using the TDP API in a JSON file containing the keys "
            "'api_url', 'org' and 'auth_token'. Provide either this or the equivalent "
            "environment variables to use the `--download` flag."
        ),
        type=argparse.FileType("r"),
        required=False,
        default=None,
    )
    args = parser.parse_args()

    if args.config is not None and not args.download:
        # Validate `download` is required when `config` is used
        raise argparse.ArgumentError(
            argument=download_action,
            message=(
                "When the config argument is used, the download flag is required: "
                "Add `-d` to the command."
            ),
        )

    if args.download:
        # Get previous IDS from API download, or skip "previous IDS" features if there
        # is no matching previous IDS
        api_config = tdp_api.APIConfig.from_json_or_env(
            json.load(args.config) if args.config else None
        )
        result = validate_ids_using_tdp_artifact(
            ids_dir=args.ids_dir, api_config=api_config
        )
    else:
        # When previous_ids_dir is None, this will validate without "previous IDS" features
        result = validate_ids(
            ids_dir=args.ids_dir, previous_ids_dir=args.previous_ids_dir
        )

    return_code = 0 if result else 1

    sys.exit(return_code)


if __name__ == "__main__":
    main()
