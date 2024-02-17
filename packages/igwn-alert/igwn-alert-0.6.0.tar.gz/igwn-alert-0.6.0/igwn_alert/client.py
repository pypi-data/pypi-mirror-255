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

import logging
import json
import hop
import sys
import warnings

from json import JSONDecodeError
from adc.errors import KafkaException
from hop import Stream, list_topics  # noqa: F401
from hop.auth import Auth
from hop.models import JSONBlob
from safe_netrc import netrc
from urllib.parse import urlparse, ParseResult
from datetime import timedelta
from time import sleep


__all__ = ('client', 'DEFAULT_SERVER',
           'DEFAULT_PORT', 'DEFAULT_GROUP',
           'DEFAULT_LISTEN_RETRIES', 'DEFAULT_RETRY_WAIT')


log = logging.getLogger(__name__)

DEFAULT_SERVER = 'kafka://kafka.scimma.org/'
DEFAULT_PORT = 9092
DEFAULT_GROUP = 'gracedb'
DEFAULT_BATCH_SIZE = 1
DEFAULT_BATCH_TIMEOUT = timedelta(seconds=0.2)
DEFAULT_LISTEN_RETRIES = 3
DEFAULT_RETRY_WAIT = 0.1


class client(Stream):
    """A hop-scotch client configured for igwn_alerts from GraceDB

    Parameters
    ----------
    username : str (optional)
        The SCIMMA username, or :obj:`None` to look up with hop auth or netrc
    password : str (optional)
        The SCIMMA password, or :obj:`None` to look up with hop auth or netrc
    auth : :class:`Auth <hop.auth.Auth>` (optional)
        A :code:`hop.auth.Auth` object.
    authfile : str (optional)
        Path to hop :code:`auth.toml`
    noauth : bool (optional)
        Set to `True` for unauthenticated session
    group : str (optional)
        GraceDB group (e.g., `gracedb`, `gracedb-playground`)
    consumer_group : str (optional)
        The consumer group ID to use for consuming messages. This can be used
        across sessions to avoid missed messages as well as allowing
        load-balancing of messages across multiple consumers assigned to the
        same consumer group. If not set, one will be randomly generated.
    server : str (optional)
        The server host (i.e., kafka://.....)
    port : int (optional)
        The server port
    batch_size : int (optional)
        The number of messages to request per batch. Higher values
        may be more efficient, but may add latency
    batch_timeout : timedelta (optional)
        How long the client waits to gather a full batch of messages.
        Higher values may be more efficient, but may add latency
    retry_on_fatal : bool (optional)
        Listening client should reconnect on fatal KafkaExceptions
        Default: false
    listen_retries: int (optional)
        Number of times to retry on fatal KafkaException
        Default: 3
    retry_wait: float (optional)
        Time to wait before retrying on fatal KafkaException
        Default: 0.1

    Example
    -------

    Here is an example for listing topics:

    .. code-block:: python

        alert_client = client(group='gracedb-test')
        topics = alert_client.get_topics()

    Here is an example for running a listener.

    .. code-block:: python

        def process_alert(topic, payload):
            if topic == 'cbc_gstlal':
                alert = json.loads(payload)
                ...

        client = IGWNAlertClient(group='gracedb-test')
        topics = ['superevent', 'cbc_gstlal']
        client.listen(process_alert, topics)

    """

    def __init__(self, username=None, password=None, auth=None, authfile=None,
                 noauth=False, group=DEFAULT_GROUP, consumer_group=None,
                 server=DEFAULT_SERVER, port=DEFAULT_PORT,
                 batch_size=DEFAULT_BATCH_SIZE,
                 batch_timeout=DEFAULT_BATCH_TIMEOUT,
                 retry_on_fatal=False, listen_retries=DEFAULT_LISTEN_RETRIES,
                 retry_wait=DEFAULT_RETRY_WAIT):

        self.server = server
        self.port = port
        self.group_prefix = group
        self.consumer_group = consumer_group
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.batch_timeout = DEFAULT_BATCH_TIMEOUT
        self.retry_on_fatal = retry_on_fatal
        self.listen_retries = listen_retries
        self.retry_wait = retry_wait

        # Construct the base url prefix for this session.
        self.base_url_prefix = self._construct_base_url()

        # Initiate the session dict:
        self.sessions = {}

        # Construct hop.auth.Auth object.
        # The order it checks is:
        #   1) auth kwarg
        #   2) noauth enabled
        #   3) Username AND password
        #   4) User-desribed location of toml auth file.
        #   5) Default location of toml auth file ($HOME/.config/hop/auth.toml)
        #   6) .netrc file ($HOME/.netrc)
        hop_auth = hop.auth

        if auth is not None:
            pass
        elif noauth:
            auth = False
        elif (username and password):
            auth = Auth(username, password)
        elif bool(username) != bool(password):
            raise RuntimeError('You must provide both a username and a '
                               'password for basic authentication.')
        elif authfile:
            auth = hop_auth.load_auth(authfile)
        else:
            try:
                auth = hop_auth.load_auth()
            except Exception:
                try:
                    netrc_auth = netrc().authenticators(self.server)
                except IOError:
                    warnings.warn("No authentication found. Proceeding "
                                  "with unathenticated session")
                    auth = False
                else:
                    if netrc_auth is not None:
                        auth = Auth(netrc_auth[0], netrc_auth[2])

        # Retain the hop.auth.Auth obj
        self.auth_obj = auth

        super().__init__(auth=auth)

    def _construct_base_url(self):
        """
        Contruct the URL, port, and group path for this session
        """

        # parse server URL:
        old = urlparse(self.server)

        # construct full URL, with group prefix:
        return ParseResult(scheme=old.scheme,
                           netloc="{}:{}".format(old.hostname, self.port),
                           path=old.path + self.group_prefix,
                           params=old.params,
                           query=old.query,
                           fragment=old.fragment).geturl()

    def _construct_topic_url(self, topics):
        """
        Construct the full URL, given a list of topics,
        or single topic.
        """

        if isinstance(topics, str):
            topics = [topics]

        url = urlparse(self.base_url_prefix)
        delimiter = ',' + url.path[1:] + '.'

        return ParseResult(scheme=url.scheme,
                           netloc=url.netloc,
                           path=url.path + '.' + delimiter.join(topics),
                           params=url.params,
                           query=url.query,
                           fragment=url.fragment).geturl()

    def listen(self, callback=None, topic=None):
        """
        Set a callback to be executed for each pubsub item received.

        Parameters
        ----------
        callback : callable (optional)
            A function of two arguments: the topic and the alert payload.
            When set to :obj:`None`, print out alert payload.
        topic : :obj:`str`, or :obj:`list` of :obj:`str` (optional)
            Topic or list of topics to listen to. When set to :obj:`None`,
            then listen to all topics connected to user's credential.
        """

        if topic:
            if isinstance(topic, str):
                topic = [topic]
            listen_topics = topic
            log.info('Listening to all {num} topics '
                     'on {server}'.format(num=len(listen_topics),
                                          server=self.server))
        else:
            listen_topics = self.get_topics()
            log.info('Listening to all {num} available topics '
                     'on {server}'.format(num=len(listen_topics),
                                          server=self.server))

        # construct the listening url:
        url = self._construct_topic_url(listen_topics)

        # Start the retriable listening routine:
        fatal_restart_attempts = 1
        fatal_restart_running = True

        while fatal_restart_running:

            # Start to listen:
            listening = True
            while listening:
                # open the stream:
                listen_stream = \
                    self.open(url, "r", group_id=self.consumer_group)
                try:
                    with listen_stream as s:
                        for payload, metadata in s.read(
                                metadata=True,
                                batch_size=self.batch_size,
                                batch_timeout=self.batch_timeout):

                            log.info('New message from topic {}'.format(
                                     metadata.topic))

                            # Fix in case message is in new format:
                            if isinstance(payload, JSONBlob):
                                payload = payload.content
                            else:
                                try:
                                    payload = json.loads(payload)
                                except (JSONDecodeError, TypeError) as e:
                                    warnings.warn("Payload is not valid "
                                                  "json: {}".format(e))

                            # If a new message came in successfully, then reset
                            # the restart counter.
                            fatal_restart_attempts = 1

                            if not callback:
                                print("New message from topic {topic}: {msg}"
                                      .format(topic=metadata.topic,
                                              msg=payload))
                            else:
                                callback(topic=metadata.topic.split('.')[1],
                                         payload=payload)
                except (KeyboardInterrupt, SystemExit):
                    listen_stream.close()
                    sys.exit(0)
                except KafkaException as e:
                    # check to see if it's a fatal error, and if so
                    # close the stream to stop lisening:
                    if e.fatal:

                        log.warning(f'fatal error from kafka: {e} '
                                    f'on attempt {fatal_restart_attempts}')
                        listening = False
                        listen_stream.close()

                        # retry logic:
                        sleep(self.retry_wait)
                        fatal_restart_attempts += 1
                        if ((fatal_restart_attempts > self.listen_retries)
                            or not self.retry_on_fatal):
                            fatal_restart_running = False
                            log.critical('Maximum number of retries reached '
                                         'or not attempted on fatal '
                                         'KafkaExceptions. Shuting down and '
                                         'raising exception.')
                            listen_stream.close()
                            raise
                    else:
                        log.warning("Non-Fatal KafkaException: {}".format(e))

    def connect(self, topics):
        """
        Takes in a topic or list of topics. Create writable
        stream objects for each of the topics in the list.

        Must have publish rights on topic.

        Parameters
        ----------
        topic : :obj:`str`, or :obj:`list` of :obj:`str`
            Topic or list of topics to publish to
        """

        if isinstance(topics, str):
            topics = [topics]

        # populate the session dict with new sessions:

        for topic in topics:
            self.sessions[topic] = self.open(self._construct_topic_url(topic),
                                             "w")

        log.info(f'Connected to topics: {topics}')

    def publish_to_topic(self, topic, msg):
        """
        Publish to a specific topic after a session
        has been connected with client.connect()

        Parameters
        ----------
        topic : :obj:`str`
            Topic name to publish to

        msg : :obj:`str`
            A message to publish to a topic

        """

        if not self.sessions:
            raise RuntimeError('No active sessions. Please '
                               'connect before publishing to a topic.')

        # Write something:
        try:
            self.sessions[topic].write(msg)
        except KeyError:
            raise RuntimeError(f'Not connected to topic {topic}. Please '
                               'connect before publishing to a topic.')

        log.info(f'Published {msg} to topic {topic}')

    def flush_by_topic(self, topic):
        """
        Flush the stream session for a specific topic after the
        session has been connected with client.connect()

        Parameters
        ----------
        topic : :obj:`str`
            Topic name to publish to

        """

        if not self.sessions:
            raise RuntimeError('No active sessions. Please '
                               'connect before publishing to a topic.')
        try:
            self.sessions[topic].flush()
        except KeyError:
            raise RuntimeError(f'Not connected to topic {topic}. Please '
                               'connect before publishing to a topic.')

        log.info(f'Flushed topic {topic}')

    def disconnect(self, topics=None):
        """
        Close all the current stream, or optionally close a single
        or list of topics

        Parameters
        ----------
        topic : :obj:`str`, or :obj:`list` of :obj:`str` (optional)
            Topic or list of topics to disconnect from. If None, then
            disconnect from all topics.

        """

        if not topics:
            for topic, session in self.sessions.items():
                session.close()
        else:
            if isinstance(topics, str):
                topics = [topics]
            for topic in topics:
                try:
                    self.sessions[topic].close()
                    self.sessions.pop(topic)
                except Exception:
                    warnings.warn("Not currently connected to "
                                  "topic {}".format(topic))

        log.info(f'Disconnected from topics {topics}')

    def publish(self, topic, msg=None):
        """
        Send an alert without pre-establishing a session.

        Parameters
        ----------
        topic : :obj:`str`, or :obj:`list` of :obj:`str` (optional)
            Topic or list of topics to publish to.

        msg : :obj:`str`
            A message to publish to a topic
        """

        with self.open(self._construct_topic_url(topic), "w") as s:
            s.write(msg)

    def get_topics(self, group=None):
        """
        Get a list of all available pubsub topics.

        Parameters
        ----------
        group : :obj:`str` (optional)
            Group prefix (e.g., "gracedb", "gracedb-playground") to show
            topics for. If :obj:`None`, list topics for the current group.

        """

        # Get the gracedb group from the argument, or from the
        # current session.

        if not group:
            group = self.group_prefix

        # Get the dict of topics from the server. convert the keys to a list.
        # Note: self.auth currently returns a list. FIXME: for now return the
        # first item in the list. Assumes only one credential, i guess.

        lt = hop.list_topics
        if not self.auth:
            all_topics = list(lt.list_topics(url=self.server,
                              auth=self.auth).keys())
        else:
            all_topics = list(lt.list_topics(url=self.server,
                              auth=self.auth[0]).keys())

        return [topic.split('.')[1] for topic in all_topics if
                group + '.' in topic]

    def get_subscriptions(self):
        """
        Get a list of your subscriptions.
        """
        warnings.warn("This feature is deprecated. Please refer "
                      "to the client.listen() method", DeprecationWarning)

    def subscribe(self, *topics):
        """
        Subscribe to one or more pubsub topics.
        """
        warnings.warn("This feature is deprecated. Please supply"
                      "list of topics to client.listen(), "
                      "and ensure you have permission to read "
                      "from topics.", DeprecationWarning)

    def unsubscribe(self, *topics):
        """
        Unsubscribe from one or more pubsub topics.
        """
        warnings.warn("This feature is deprecated.", DeprecationWarning)

    def delete(self):
        """
        Delete a pubsub topic
        """
        warnings.warn("This feature is deprecated.", DeprecationWarning)
