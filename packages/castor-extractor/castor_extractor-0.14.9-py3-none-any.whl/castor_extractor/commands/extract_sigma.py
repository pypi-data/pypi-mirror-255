import logging
from argparse import ArgumentParser

from castor_extractor.visualization import sigma  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main():
    parser = ArgumentParser()

    parser.add_argument("-H", "--host", help="Sigma host")
    parser.add_argument("-c", "--client-id", help="Sigma client ID")
    parser.add_argument("-a", "--api-token", help="Generated API key")
    parser.add_argument("-o", "--output", help="Directory to write to")

    args = parser.parse_args()
    sigma.extract_all(
        host=args.host,
        client_id=args.client_id,
        api_token=args.api_token,
        output_directory=args.output,
    )
