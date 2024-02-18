import logging
from argparse import ArgumentParser

from castor_extractor.visualization import salesforce_reporting  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main():
    parser = ArgumentParser()

    parser.add_argument("-u", "--username", help="Salesforce username")
    parser.add_argument("-p", "--password", help="Salesforce password")
    parser.add_argument("-k", "--consumer-key", help="Salesforce consumer key")
    parser.add_argument(
        "-s", "--consumer-secret", help="Salesforce consumer secret"
    )
    parser.add_argument(
        "-t", "--security-token", help="Salesforce security token"
    )
    parser.add_argument("-l", "--url", help="Salesforce instance URL")
    parser.add_argument("-o", "--output", help="Directory to write to")

    args = parser.parse_args()
    salesforce_reporting.extract_all(
        username=args.username,
        password=args.password,
        consumer_key=args.consumer_key,
        consumer_secret=args.consumer_secret,
        security_token=args.security_token,
        instance_url=args.url,
        output_directory=args.output,
    )
