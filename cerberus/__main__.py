import time
from argparse import ArgumentParser
from multiprocessing import Process
from random import shuffle

from cerberus.clients import Puller, Pusher
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

    def __init__(self, hostname):
        self.admin = AdminClient(hostname)

    def next(self, seqid, channel):
        name = 'user-{}'.format(seqid)
        password = 'password'
        self.admin.add_user(name=name, password=password, channels=[channel])
        return name, password


class Cerberus:

    RAMPUP_INTERVAL = 4
    DOCS_PER_PUSHER = 10 ** 6

    def __init__(self, hostname):
        self.clients = []
        self.hostname = hostname

    def get_puller(self, name, password):
        puller = Puller(hostname=self.hostname, name=name, password=password)
        return Process(target=puller)

    def get_pusher(self, name, password, channel, seqid):
        pusher = Pusher(self.hostname, name=name, password=password)
        return Process(target=pusher,
                       args=(channel,
                             seqid * self.DOCS_PER_PUSHER,
                             (seqid + 1) * self.DOCS_PER_PUSHER
                             )
                       )

    def init_clients(self, num_pullers, num_pushers):
        client_id = 0
        pusher_id = 0
        channels = Channels()
        users = Users(self.hostname)
        clients = ['puller'] * num_pullers + ['pusher'] * num_pushers
        shuffle(clients)

        for client in clients:
            channel = channels.next()
            name, password = users.next(client_id, channel)
            if client == 'puller':
                process = self.get_puller(name, password)
            else:
                process = self.get_pusher(name, password, channel, pusher_id)
                pusher_id += 1
            client_id += 1
            self.clients.append(process)

    def __call__(self):
        for client in self.clients:
            client.start()
            time.sleep(self.RAMPUP_INTERVAL)

        for client in self.clients:
            client.join()


def main():
    parser = ArgumentParser(prog='cerberus')
    parser.add_argument('--pullers', dest='pullers', type=int, required=True)
    parser.add_argument('--pushers', dest='pushers', type=int, required=True)
    parser.add_argument('hostname', nargs=1)
    args = parser.parse_args()

    c = Cerberus(hostname=args.hostname[0])
    c.init_clients(num_pullers=args.pullers, num_pushers=args.pushers)
    c()


if __name__ == '__main__':
    main()
