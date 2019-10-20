import logging
import sys
from typing import Optional

from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError

from constants import DISCOURSE_CREDENTIALS
from utils import render

import locale
import argparse

locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")


def test_login(client: DiscourseClient) -> None:
    try:
        client.latest_topics()
    except DiscourseClientError as e:
        logging.error(f"Could not perform login: {e}")
        sys.exit(-1)


def disable_request(client: DiscourseClient, disable_verb: Optional[str] = None, disable_path: Optional[str] = None):
    original_request = client._request

    def new_request_fn(verb, path, *args, **kwargs):
        if disable_verb and verb == disable_verb or disable_path and path == disable_path:
            logging.info(f'Dry run. {verb} request to {path} was not made')
            return
        original_request(verb, path, *args, **kwargs)

    client._request = new_request_fn


def main():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s", level=logging.INFO
    )

    assert DISCOURSE_CREDENTIALS[
        "api_key"
    ], "Environment variable DISCOURSE_API_KEY not set"

    parser = argparse.ArgumentParser(
        description='Updates voucher post, sends out vouchers via PM, receives returned vouchers via PM'
    )
    parser.add_argument('--dry', action='store_true', help='do not execute POST or PUT requests')

    args = parser.parse_args()

    client = DiscourseClient(**DISCOURSE_CREDENTIALS)
    if args.dry:
        disable_request(client, 'POST')
        disable_request(client, 'PUT')

    test_login(client)

    post_content = render('voucher_table.md')
    client.update_post(24763, post_content)  # https://forum.flipdot.org/t/voucher-36c3/3432/4


if __name__ == "__main__":
    main()
