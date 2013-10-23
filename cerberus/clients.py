import time
from random import uniform
from uuid import uuid4

from cerberus.rest import SyncGatewayClient


class DocIterator:

    def __init__(self, channel, starts_at, ends_at):
        self.channel = channel
        self.starts_at = starts_at
        self.ends_at = ends_at

    @staticmethod
    def uhex():
        return uuid4().hex

    def __iter__(self):
        for i in range(self.starts_at, self.ends_at):
            docid = self.uhex()
            yield docid, {'_id': 'doc-{}'.format(i),
                          'channels': [self.channel],
                          'data': docid}


class Pusher(SyncGatewayClient):

    def __call__(self, channel, sleep_interval, starts_at, ends_at):
        for docid, doc in DocIterator(channel=channel,
                                      starts_at=starts_at, ends_at=ends_at):
            self.put_single_doc(docid=docid, doc=doc)
            time.sleep(uniform(sleep_interval * 0.8, sleep_interval * 1.2))


class Puller(SyncGatewayClient):

    def __call__(self):
        self.last_seq = '*:{}'.format(self.get_last_seq())
        while True:
            feed = self.get_changes_feed(since=self.last_seq)
            for result in feed['results']:
                self.get_single_doc(result['id'])
            self.last_seq = feed['last_seq']
