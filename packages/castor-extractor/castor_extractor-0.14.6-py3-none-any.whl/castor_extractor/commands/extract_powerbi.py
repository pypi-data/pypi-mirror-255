import logging
from argparse import ArgumentParser

from castor_extractor.visualization import powerbi  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main():
    parser = ArgumentParser()

    parser.add_argument("-t", "--tenant_id", help="PowerBi tenant ID")
    parser.add_argument("-c", "--client_id", help="PowerBi client ID")
    parser.add_argument("-s", "--secret", help="PowerBi password")
    parser.add_argument(
        "-sc",
        "--scopes",
        help="PowerBi scopes, optional",
        nargs="*",
    )
    parser.add_argument("-o", "--output", help="Directory to write to")

    args = parser.parse_args()
    powerbi.extract_all(
        tenant_id=args.tenant_id,
        client_id=args.client_id,
        secret=args.secret,
        scopes=args.scopes,
        output_directory=args.output,
    )
