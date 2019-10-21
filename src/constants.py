import os

DISCOURSE_CREDENTIALS = {
    'api_key': os.getenv('DISCOURSE_API_KEY'),
    'api_username': 'flipbot',
    'host': 'https://forum.flipdot.org'
}

VOUCHER_CONFIG_PATH = 'voucher.yml'
VOUCHER_TABLE_POST_ID = 24763  # https://forum.flipdot.org/t/voucher-36c3/3432/4
