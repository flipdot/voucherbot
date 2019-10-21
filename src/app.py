import logging
import re
import sys
from typing import Optional, List  # , TypedDict

from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError

from constants import DISCOURSE_CREDENTIALS, VOUCHER_CONFIG_PATH
from utils import render

import locale
import argparse
import yaml

locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

# custom types
# TypedDict is only available since python 3.8
# class VoucherConfigElement(TypedDict):
#     voucher: str
#     owner: Optional[str]
#     message_id: Optional[int]
#     persons: Optional[int]
from typing import Dict

VoucherConfigElement = Dict

VoucherConfig = List[VoucherConfigElement]


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
            logging.info(f'Dry run. {verb} request to {path} was not made. Data:')
            logging.info(kwargs.get('data'))
            return {}
        return original_request(verb, path, *args, **kwargs)

    client._request = new_request_fn


def read_voucher_config() -> VoucherConfig:
    with open(VOUCHER_CONFIG_PATH) as f:
        conf = yaml.safe_load(f)
    return conf


def write_voucher_config(config: VoucherConfig, path=VOUCHER_CONFIG_PATH) -> None:
    with open(path, 'w') as f:
        yaml.safe_dump(config, f)


def get_username(voucher: VoucherConfigElement) -> Optional[str]:
    owner = voucher['owner']
    return re.search(r'@([^ ]+)', owner)[1] if owner else None


def send_voucher_to_user(client: DiscourseClient, voucher: VoucherConfigElement):
    username = get_username(voucher)
    message_content = render('voucher_message.md', voucher=voucher)
    logging.info(f'Sending voucher to {username}')
    res = client.create_post(message_content, title='Dein 36C3 Voucher', archetype='private_message',
                             target_usernames=username)
    message_id = res.get('topic_id')
    logging.info(f'Sent, message_id is {message_id}')
    voucher['message_id'] = message_id


def send_message_to_user(client: DiscourseClient, voucher: VoucherConfigElement, message: str) -> None:
    username = get_username(voucher)
    message_id = voucher.get('message_id')
    if not message_id:
        return
    logging.info(f'Sending message to {username} (Thread {message_id})')
    client.create_post(message, topic_id=message_id)


def check_for_returned_voucher(client: DiscourseClient, voucher: VoucherConfigElement) -> Optional[str]:
    message_id = voucher['message_id']
    posts = client.posts(message_id)
    user_posts = [post for post in posts['post_stream']['posts'] if post['name'] != 'flipbot']
    user_posts_content = ' '.join([p['cooked'] for p in user_posts])
    new_voucher = re.search(r'CHAOS[a-zA-Z0-9]+', user_posts_content)
    if new_voucher:
        return new_voucher[0]


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
    parser.add_argument('--broadcast', type=str, help='send a message to all voucher owners')

    args = parser.parse_args()

    client = DiscourseClient(**DISCOURSE_CREDENTIALS)
    if args.dry:
        disable_request(client, 'POST')
        disable_request(client, 'PUT')

    test_login(client)

    vouchers = read_voucher_config()

    for voucher in vouchers:
        if not voucher['owner']:
            continue
        if voucher.get('message_id'):
            new_voucher_code = check_for_returned_voucher(client, voucher)
            if new_voucher_code:
                logging.info(f'Voucher returned by {get_username(voucher)}')
                send_message_to_user(client, voucher, message=f'Prima, vielen Dank für "{new_voucher_code}"!')
                voucher['voucher'] = new_voucher_code
                voucher['owner'] = None
                voucher['message_id'] = None
                voucher['persons'] = None
            if args.broadcast:
                send_message_to_user(client, voucher, message=args.broadcast)
        else:
            send_voucher_to_user(client, voucher)

    post_content = render('voucher_table.md', vouchers=vouchers)
    client.update_post(24763, post_content)  # https://forum.flipdot.org/t/voucher-36c3/3432/4

    if args.dry:
        logging.info(f'Dry run: Config written to voucher_dryrun.yml instead of {VOUCHER_CONFIG_PATH}')
        write_voucher_config(vouchers, 'voucher_dryrun.yml')
    else:
        write_voucher_config(vouchers)


if __name__ == "__main__":
    main()
