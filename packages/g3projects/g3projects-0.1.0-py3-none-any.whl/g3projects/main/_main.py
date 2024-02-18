import argparse

from ..logical import generate_logical_files
from ..physical import generate_physical_files


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Create a G3 Project PLC files from a SystemConfig.json file.'
            )
        )
    parser.add_argument(
        '-s',
        '--system-config',
        type=argparse.FileType('r'),
        required=True,
        help='Path to the SystemConfig.json file'
        )
    return parser.parse_args()


def generate_project_files(system_config_path: str) -> None:
    generate_logical_files(system_config_path)
    generate_physical_files(system_config_path)


def main() -> None:
    args = parse_arguments()
    generate_project_files(args.system_config)


if __name__ == "__main__":
    main()
