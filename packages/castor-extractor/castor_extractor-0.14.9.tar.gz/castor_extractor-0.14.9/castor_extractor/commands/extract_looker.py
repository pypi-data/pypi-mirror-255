from argparse import ArgumentParser

from castor_extractor.visualization import looker  # type: ignore


def main():
    parser = ArgumentParser()
    parser.add_argument("-b", "--base-url", help="Looker base url")
    parser.add_argument("-u", "--username", help="Looker client id")
    parser.add_argument("-p", "--password", help="Looker client secret")
    parser.add_argument("-o", "--output", help="Directory to write to")
    parser.add_argument("-t", "--timeout", type=int, help="Timeout in seconds")
    parser.add_argument(
        "--thread-pool-size",
        type=int,
        help="Thread pool size, if searching per folder",
    )
    parser.add_argument(
        "--safe-mode",
        "-s",
        help="Looker safe mode",
        action="store_true",
    )
    parser.add_argument(
        "--log-to-stdout",
        help="Send all log outputs to stdout instead of stderr",
        action="store_true",
    )

    parser.add_argument(
        "--search-per-folder",
        help="Fetches Looks and Dashboards per folder",
        action="store_true",
    )

    args = parser.parse_args()

    looker.extract_all(
        base_url=args.base_url,
        client_id=args.username,
        client_secret=args.password,
        log_to_stdout=args.log_to_stdout,
        output_directory=args.output,
        safe_mode=args.safe_mode,
        search_per_folder=args.search_per_folder,
        thread_pool_size=args.thread_pool_size,
        timeout=args.timeout,
    )
