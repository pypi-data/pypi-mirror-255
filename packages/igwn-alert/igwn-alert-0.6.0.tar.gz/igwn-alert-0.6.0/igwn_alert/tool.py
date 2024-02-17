# Copyright (C) Alexander Pace (2021)
# Copyright (C) Duncan Meacher (2021)
#
# This file is part of igwn_alert
#
# igwn_alert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with igwn_alert.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import argparse
import logging
import json

from hop import auth as hop_auth
from safe_netrc import netrc

from igwn_alert import client, DEFAULT_SERVER, DEFAULT_GROUP, \
    DEFAULT_PORT, DEFAULT_LISTEN_RETRIES, DEFAULT_RETRY_WAIT
from igwn_alert.version import __version__


# Version string
VERSION_STRING = "igwn-alert client {0}".format(__version__)

# Get logger:
logger = logging.getLogger("igwn_alert")


def parser():
    parser = argparse.ArgumentParser(prog='igwn-alert')
    parser.add_argument("--no-auth", action="store_true",
                        help="If set, disable authentication.")
    parser.add_argument('-g', '--group', default=DEFAULT_GROUP,
                        help='GraceDB group name (e.g., gracedb, '
                             'gracedb-playground)')
    parser.add_argument('-c', '--consumer-group',
                        help='Consumer group ID to use for consuming '
                             'messages across sessions')
    parser.add_argument('-l', '--log', help='Log level', default='error',
                        choices='critical error warning info debug'.split())
    parser.add_argument('-n', '--netrc',
                        help='netrc file (default: read from NETRC '
                        'environment variable or ~/.netrc)')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT,
                        help='igwn-alert server port')
    parser.add_argument('-r', '--retry-on-fatal', default=False,
                        action='store_true',
                        help='reconnect listener on fatal exceptions')
    parser.add_argument('-s', '--server', default=DEFAULT_SERVER,
                        help='igwn-alert server hostname')
    parser.add_argument('-t', '--listen_retries',
                        default=DEFAULT_LISTEN_RETRIES,
                        help='fatal reconnect retry attempts')
    parser.add_argument('-u', '--username',
                        help='User name (default: look up in auth.toml '
                              'or .netrc)')
    parser.add_argument('-w', '--retry_wait', default=DEFAULT_RETRY_WAIT,
                        help='fatal reconnect retry attempts')
    parser.add_argument('-V', '--version', action='version',
                        version=VERSION_STRING)

    subparsers = parser.add_subparsers(dest='action', help='sub-command help')
    subparsers.required = True

    subparser = subparsers.add_parser(
        'listen', help='Listen for igwn-alert messages and print '
                       'them to stdout.')
    subparser.add_argument(
        'topics', nargs='*', help='a pubsub topic or list of topics '
                                  '(e.g. cbc_gstlal)')

    subparser = subparsers.add_parser(
        'subscriptions', help='List your subscriptions')

    subparser = subparsers.add_parser(
        'topics', help='List available pubsub topics')

    subparser = subparsers.add_parser(
        'unsubscribe', help='Unsubscribe from one or more topics')

    subparser = subparsers.add_parser(
        'send', help='publish contents of a file to a pubsub topic')
    subparser.add_argument(
        'topic', nargs='+', help='a pubsub topic (e.g. cbc_gstlal)')
    subparser.add_argument(
        'alertfile', nargs='+', help='name of the file with the alert to send',
        type=argparse.FileType('rb'))
    return parser


def main(args=None):
    opts = parser().parse_args(args)

    if opts.log is not None:
        logging.basicConfig(level=opts.log.upper())

    if opts.no_auth:
        auth = False
    elif opts.username:
        all_auth = hop_auth.load_auth()
        auth = hop_auth.select_matching_auth(all_auth, opts.server,
                                             opts.username)
    elif opts.netrc:
        netrc_auth = netrc().authenticators(opts.server)
        if netrc_auth is None:
            raise KeyError(
                f"netrc information for {opts.server} could not be found")
        auth = hop_auth.Auth(netrc_auth[0], netrc_auth[2])
    else:
        auth = None

    lv = client(server=opts.server,
                port=opts.port,
                group=opts.group,
                auth=auth,
                consumer_group=opts.consumer_group,
                retry_on_fatal=opts.retry_on_fatal,
                listen_retries=opts.listen_retries,
                retry_wait=opts.retry_wait)

    try:
        if opts.action == 'listen':
            lv.listen(callback=None, topic=[*opts.topics])
        if opts.action == 'topics':
            print("Topics for group {0} associated with the current "
                  "credential:".format(opts.group))
            print(*lv.get_topics(), sep='\n')
        elif opts.action == 'subscriptions':
            raise DeprecationWarning('This feature is deprecated. '
                                     'Please refer to the get_topics() API '
                                     'command or the SCIMMA auth interface.')
        elif opts.action == 'subscribe':
            raise DeprecationWarning('This feature is deprecated. '
                                     'Please refer to the listen() API '
                                     'command or "listen" CLI command.')
        elif opts.action == 'unsubscribe':
            raise DeprecationWarning('This feature is deprecated.')
        elif opts.action == 'send':
            for openfile in opts.alertfile:
                eventfile = openfile.read().decode('utf-8')
                try:
                    alert = json.dumps(eventfile)
                except Exception:
                    alert = eventfile
                lv.publish(topic=opts.topic, msg=alert)
                openfile.close()
    except (KeyboardInterrupt, SystemExit):
        pass
