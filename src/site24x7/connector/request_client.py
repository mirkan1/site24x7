import requests
from .models.model import ClientModel

class RequestClient(ClientModel):
    '''cache client is a client model that is used to store data in a cache file'''
    def __init__(self, *args, headers=None, auth=None, data=None, **kwargs):
        self.dict = {}
        self.auth = auth
        self.data = data
        if not headers:
            self.headers = {'Content-Type': 'application/json'}
        elif isinstance(headers, dict):
            self.headers = headers
        else:
            raise Exception("headers must be a dict") from None
        super().__init__(self.dict, *args, **kwargs)

    def get(self, url, **kwargs):
        '''get the data from the url'''
        headers = kwargs.get('headers', self.headers)
        data = kwargs.get('data', self.data)
        auth = kwargs.get('auth', self.auth)
        return requests.get(url, headers=headers, data=data, auth=auth)

    def post(self, url, **kwargs):
        '''post the data to the url'''
        headers = kwargs.get('headers', self.headers)
        data = kwargs.get('data', self.data)
        auth = kwargs.get('auth', self.auth)
        return requests.post(url, headers=headers, data=data, auth=auth)

    def delete(self, url, **kwargs):
        '''delete the data from the url'''
        headers = kwargs.get('headers', self.headers)
        data = kwargs.get('data', self.data)
        auth = kwargs.get('auth', self.auth)
        return requests.delete(url, headers=headers, data=data, auth=auth)

    def put(self, url, **kwargs):
        '''put the data to the url'''
        headers = kwargs.get('headers', self.headers)
        data = kwargs.get('data', self.data)
        auth = kwargs.get('auth', self.auth)
        return requests.put(url, headers=headers, data=data, auth=auth)

    def setRequestData(self, data):
        '''sets the data for the next api call'''
        self.data = data

    def setRequestDHeaders(self, headers):
        '''sets the headers for the next api call'''
        self.headers = headers
