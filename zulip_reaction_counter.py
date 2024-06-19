#!/usr/bin/env python3

"""Count reactions in Zulip and produce a report on these.
"""

import argparse
from csv import writer
from functools import cache
from pprint import pprint
import sys

import zulip

__version__ = '0.1.0'

@cache
def get_user_name(client, user_id):
    """Return username of a given user_id (caching the result)"""
    result = client.get_user_by_id(user_id)
    return result['user']['full_name']


def main():
    description = """\
Count reactions from a Zulip realm.  This outputs a csv file that gives
(stream, message_sender, reactor, emoji_name, timestamp), which can be further
processed yourself.
"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('zuliprc', help="zuliprc file to use to connect")
    parser.add_argument('--narrow', default="streams:public", help='Select messages based on this narrow (search filter).  This value is split by spaces and then by the ":" symbol to send to the API.  You should include either "streams:" or "stream:" to force a search of all history, not only the history of the API user.  For searching based on search terms, you can use "search:TERM".  For zulip>9.0, you can include "has:reaction". (default "%(default)s)"')
    parser.add_argument('--chunk-size', default=1000, type=int, help="Chunk size for pagination (default %(default)s)")
    parser.add_argument('--no-header', action='store_true', help="Don't print a CSV header")
    parser.add_argument('--verbose', '-v', action='store_true', help="Be more verbose (on stderr)")
    args = parser.parse_args()

    # Initial i/o setup
    client = zulip.Client(config_file="~/zuliprc")
    if not args.no_header:
        print("#stream,sender,reactor,reaction,timestamp", file=sys.stdout)
    write = writer(sys.stdout, dialect='excel')

    # Cache stream info
    result = client.get_streams(
        include_public=True,
        include_subscribed=False,
        )
    STREAMS = {x['stream_id']: x['name'] for x in result['streams']}

    # Our initial request (gets updated in-place for future requests for
    # pagination)
    request = {
        "anchor": "newest",
        "num_before": args.chunk_size,
        "num_after": 0,
        "include_anchor": True,
        #"narrow": [{"operator":"channels", "operand": "public"}],
        "narrow": [
            {"operator":x.split(':')[0], "operand": x.split(':', 1)[1]}
            for x in args.narrow.split()],
        }

    # Do our pagination (until we are out)
    n_messages = 0
    while True:
        result = client.get_messages(request)
        if args.verbose:
            pprint(result, stream=sys.stderr)
            print(len(result['messages']))
        n_messages += len(result['messages'])
        for message in reversed(result['messages']):
            sname = message['sender_full_name']
            stream_id = message['stream_id']
            stream_name = STREAMS[stream_id]
            time = message['timestamp'] # unix time
            for reaction in message['reactions']:
                remoji = reaction['emoji_name']
                ruser = reaction['user_id']
                rname = get_user_name(client, ruser)

                write.writerow((stream_name, sname, rname, remoji, time))

        print("Processed %d messages so far"%n_messages, file=sys.stderr)

        if result['found_oldest']:
            break
        request["include_anchor"] = False  # future ones exclude the anchor
        request["anchor"] = result['messages'][0]['id']
        #break


if __name__ == "__main__":
    main()
