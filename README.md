# voucherbot for discourse

The voucherbot manages the distribution of vouchers via Discourse. It was originally created for distributing the
vouchers for the 36C3.

A voucher is usable a single time, but replicates itself. The idea is therefore to pass the generated tokens to your
friends.

We, flipdot, receive a list of vouchers. We distribute them via Discourse to our members, who can then pass them
to their friends. As soon as all their friends bought their ticket, they should send them back to us, so we can
distribute it to another member.

This bot simplifies this process by automating parts of it. A yaml file serves as a database, containing a mapping
of vouchers and member accounts. 

## Features

- Updates a post in the forum. The post contains a table with the information which member received a vouchers
- Sends the voucher via forum message to the member
- Receives a returned voucher and updates the yaml file with the new one
- Broadcast: Allows to send a message to all current voucher owners

## Usage

Python 3.7 required (TODO: require 3.8 to be able to use TypedDict eventually)

Copy `example_voucher.yml` to `voucher.yml`. Enter your vouchers. Make a backup of this file (we do not make one for
you and we **WILL** modify this file. Don't cry if something get's lost).

Open `constants.py` and change `VOUCHER_TABLE_POST_ID`. This post will be constantly updated with the table of members
who currently own a voucher.

    pip install -r requirements.txt
    DISCOURSE_API_KEY=deadbeef python src/app.py --dry  # leave out --dry if you are brave