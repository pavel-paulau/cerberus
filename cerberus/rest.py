import ujson as json

import requests


class RestClient:

    def __init__(self, name=None, password=None, cookies=None):
        self.session = requests.Session()
        if name and password:
            self.session.auth = (name, password)
        if cookies:
            self.session.cookies.update(cookies)
        self.session.headers.update({'Content-type': 'application/json'})

    def post(self, url, data):
        return self.session.post(url=url, data=json.dumps(data)).content.decode('UTF-8')

    def put(self, url, data):
        return self.session.put(url=url, data=json.dumps(data)).content.decode('UTF-8')

    def get(self, url):
        return self.session.get(url=url).content.decode('UTF-8')


class SyncGatewayClient(RestClient):

    def __init__(self, hostname, name=None, password=None, cookies=None,
                 db='sync_gateway'):
        super(SyncGatewayClient, self).__init__(name, password, cookies)
        self.base_url = 'http://{}:4984/{}'.format(hostname, db)

    def put_single_doc(self, docid, doc):
        url = '{}/{}?new_edits=true'.format(self.base_url, docid)
        return self.put(url=url, data=doc)

    def get_bulk_docs(self, docs):
        url = '{}/_bulk_get'.format(self.base_url)
        return self.post(url=url, data=docs)

    def get_single_doc(self, docid):
        url = '{}/{}'.format(self.base_url, docid)
        return self.get(url=url)

    def get_last_seq(self):
        r = self.get(url=self.base_url)
        return json.loads(r)['committed_update_seq']

    def get_changes_feed(self, since=None):
        url = '{}/_changes?limit=10&feed=longpoll&since={}'.format(
            self.base_url, since)
        return json.loads(self.get(url=url))


class AdminClient(RestClient):

    def __init__(self, hostname, db='sync_gateway'):
        super(AdminClient, self).__init__()
        self.base_url = 'http://{}:4985/{}'.format(hostname, db)

    def add_user(self, name, password, channels):
        url = '{}/_user/{}'.format(self.base_url, name)
        data = {'name': name, 'password': password, 'admin_channels': channels}
        return self.put(url=url, data=data)

    def create_session(self, name):
        url = '{}/_session'.format(self.base_url, name)
        data = {'name': name, 'ttl': 2000}
        cookie = json.loads(self.post(url=url, data=data))
        return {cookie['cookie_name']: cookie['session_id']}
