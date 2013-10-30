import time
from argparse import ArgumentParser
from multiprocessing import Process
from random import shuffle

from logger import logger

from cerberus.clients import Puller, BulkPuller, Pusher
from cerberus.rest import AdminClient


class Iterator:

    def __iter__(self):
        return self


class Channels(Iterator):

    CHANNEL_QUOTA = 40

    def __init__(self):
        self.curr_channel = 0
        self.curr_users = 0

    def next(self):
        if self.curr_users < self.CHANNEL_QUOTA:
            self.curr_users += 1
            return hex(self.curr_channel)
        else:
            self.curr_channel += 1
            self.curr_users = 0
            return self.next()


class Users(Iterator):

    def __init__(self, hostname, auth):
        self.admin = AdminClient(hostname)
        self.auth = auth

    def next(self, seqid, channel):
        name = 'user-{}'.format(seqid)
        password = 'password'

        logger.info('Creating new user {}, auth by {}'.format(name, self.auth))

        self.admin.add_user(name=name, password=password, channels=[channel])
        if self.auth == 'cookie':
            cookies = self.admin.create_session(name=name)
            return {'cookies': cookies}
        else:
            return {'name': name, 'password': password}


class Cerberus:

    DOCS_PER_PUSHER = 10 ** 6

    def __init__(self, hostname, rampup_delay, sleep_interval):
        self.clients = []
        self.hostname = hostname
        self.rampup_delay = rampup_delay
        self.sleep_interval = sleep_interval

    def get_puller(self, **auth):
        puller = Puller(hostname=self.hostname, **auth)
        return Process(target=puller)

    def get_bulk_puller(self, **auth):
        puller = BulkPuller(hostname=self.hostname, **auth)
        return Process(target=puller)

    def get_pusher(self, channel, seqid, **auth):
        pusher = Pusher(self.hostname, **auth)
        return Process(target=pusher,
                       args=(channel,
                             self.sleep_interval,
                             seqid * self.DOCS_PER_PUSHER,
                             (seqid + 1) * self.DOCS_PER_PUSHER
                             )
                       )

    def init_clients(self, num_pullers, num_bulk_pullers, num_pushers, auth):
        client_id = 0
        pusher_id = 0
        channels = Channels()
        users = Users(self.hostname, auth)

        clients = ['puller'] * num_pullers + \
                  ['bulk_puller'] * num_bulk_pullers + \
                  ['pusher'] * num_pushers
        shuffle(clients)

        for client in clients:
            channel = channels.next()
            if client == 'puller':
                process = self.get_puller(**users.next(client_id, channel))
            elif client == 'bulk_puller':
                process = self.get_bulk_puller(**users.next(client_id, channel))
            else:
                process = self.get_pusher(channel, pusher_id,
                                          **users.next(client_id, channel))
                pusher_id += 1
            client_id += 1
            self.clients.append(process)

    def __call__(self):
        for i, client in enumerate(self.clients):
            logger.info('Starting new client: {}'.format(i))
            client.start()
            time.sleep(self.rampup_delay)

        for client in self.clients:
            client.join()


def main():
    parser = ArgumentParser(prog='cerberus')
    parser.add_argument('--pullers', type=int, required=True)
    parser.add_argument('--bulkpullers', type=int, required=True)
    parser.add_argument('--pushers', type=int, required=True)
    parser.add_argument('--rampup', type=float, default=3600)
    parser.add_argument('--sleep', type=float, default=10)
    parser.add_argument('--auth', type=str, choices=('cookie', 'header'))
    parser.add_argument('hostname', nargs=1)
    args = parser.parse_args()

    rampup_delay = args.rampup / (args.pullers + args.bulkpullers + args.pushers)

    c = Cerberus(hostname=args.hostname[0],
                 rampup_delay=rampup_delay, sleep_interval=args.sleep)
    c.init_clients(num_pullers=args.pullers,
                   num_bulk_pullers=args.bulkpullers,
                   num_pushers=args.pushers,
                   auth=args.auth)
    c()


if __name__ == '__main__':
    main()
