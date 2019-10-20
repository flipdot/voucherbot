import logging
import sys

from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError

from constants import DISCOURSE_CREDENTIALS
from utils import render

import locale

locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")


def test_login(client: DiscourseClient) -> None:
    try:
        client.latest_topics()
    except DiscourseClientError as e:
        logging.error(f"Could not perform login: {e}")
        sys.exit(-1)


def main():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s", level=logging.INFO
    )

    assert DISCOURSE_CREDENTIALS[
        "api_key"
    ], "Environment variable DISCOURSE_API_KEY not set"

    client = DiscourseClient(**DISCOURSE_CREDENTIALS)

    test_login(client)

    post_content = render('voucher_table.md')
    client.update_post(24763, post_content)  # https://forum.flipdot.org/t/voucher-36c3/3432/4


if __name__ == "__main__":
    main()
