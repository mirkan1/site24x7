import json
from datetime import datetime
import requests
ALL_SCOPES = "Site24x7.Account.Read, Site24x7.Account.Create, Site24x7.Account.Update, Site24x7.Account.Delete, Site24x7.Account.All, Site24x7.Reports.Read, Site24x7.Reports.Create, Site24x7.Reports.Update, Site24x7.Reports.Delete, Site24x7.Reports.All,  Site24x7.Operations.Read, Site24x7.Operations.Create, Site24x7.Operations.Update, Site24x7.Operations.Delete, Site24x7.Operations.All, Site24x7.Msp.Read, Site24x7.Msp.Create, Site24x7.Msp.Update, Site24x7.Msp.Delete, Site24x7.Msp.All, Site24x7.Bu.Read, Site24x7.Bu.Create, Site24x7.Bu.Update, Site24x7.Bu.Delete, Site24x7.Bu.All"

READ_SOPES = "Site24x7.Account.Read, Site24x7.Reports.Read, Site24x7.Operations.Read"
current_status_type = [
    'unit',
    'monitor_id',
    'name',
    'attribute_key',
    'attribute_label',
    'attributeName',
    'attribute_value',
    'monitor_type',
    'last_polled_time',
    'status',
]
class ZohoConnection:
    ''' Oath2.0 authentication flow for Zoho API '''
    MONITOR_GRUPS = {}
    MONITORS = {}
    MSP_CUSTOMERS = {}
    DEVICE_KEY = None
    def __init__(self, client_id=None, client_secret=None, code=None, refresh_token=None, access_token=None, cache=True):
        if cache:
            try:
                self.pull_data_from_cache()
            except FileNotFoundError:
                cache = False
        if not cache:
            self.client_id = client_id
            self.client_secret = client_secret
            self.refresh_token = refresh_token
            self.headers = {
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Accept": "application/json; version=2.0"
            }
            self.access_token = access_token
            self.token_type = None
            # 1 minute
            self.expration_time = datetime.now().timestamp() + 60
            self.api_domain = "https://www.site24x7.com"
            self.auth_domain = 'https://accounts.zoho.com'
            self.code = code
            if not self.refresh_token and not self.code:
                raise Exception('No refresh token or code provided')
            if not self.refresh_token and self.code:
                self.authorization_code(self.code)
            elif not access_token:
                self.refresh()
            else:
                self.headers['Authorization'] = 'Zoho-oauthtoken ' + self.access_token
            try:
                # this is still experimental
                self.set_device_key()
            except Exception as exp:
                print(exp)

    def pull_data_from_cache(self):
        ''' Pull data from cache file '''
        with open('.cache', 'r', encoding="utf-8") as cache_file:
            data = json.loads(cache_file.read())
            self.__dict__ = data

    def authorization_code(self, code):
        ''' Get access token from authorization code '''
        url = self.auth_domain + '/oauth/v2/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=data, timeout=10, headers=self.headers)
        if response.status_code == 200:
            response = json.loads(response.text)
            if "error" in response:
                raise Exception(response["error"])
            self.access_token = response['access_token']
            self.token_type = response['token_type']
            self.refresh_token = response['refresh_token']
            self.expration_time = datetime.now().timestamp() + response['expires_in']
            self.headers['Authorization'] = 'Zoho-oauthtoken ' + self.access_token

    def refresh(self):
        ''' Refresh the access token '''
        self.did_expire()
        url = self.auth_domain + '/oauth/v2/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(url, data=data, timeout=10, headers=self.headers)
        if response.status_code == 200:
            response = json.loads(response.text)
            if "error" in response:
                raise Exception(response["error"])
            self.access_token = response['access_token']
            self.token_type = response['token_type']
            self.expration_time = datetime.now().timestamp() + response['expires_in']
            self.headers['Authorization'] = 'Zoho-oauthtoken ' + self.access_token
        else:
            raise Exception('Error refreshing token')
        # save all data to a text file
        self.save_data_into_file()

    def save_data_into_file(self):
        ''' Save all data into a file '''
        with open('.cache', 'w', encoding="utf-8") as cache_file:
            cache_file.write(json.dumps(self.__dict__, indent=4))

    def get(self, url, params:dict=None) -> dict:
        ''' Get request '''
        self.refresh()
        url = self.api_domain + url
        headers = self.headers
        response = requests.get(url, params=params, headers=headers, timeout=20)
        json_response = json.loads(response.text)
        if response.status_code == 200:
            return json_response
        else:
            error_code = json_response['error_code']
            message = json_response['message']
            raise Exception(f'Error getting response with status {response.status_code}:{error_code} \
                {message}')

    def get_current_status_all(self):
        ''' Get all current from site24x7 status '''
        url = '/api/current_status'
        response = self.get(url)
        for i in response['data']['monitor_groups']:
            group_id = i['group_id']
            group_name = i['group_name']
            status = i['status']
            if "monitors" in i:
                monitors = i['monitors']
            else:
                monitors = []
            if "downMonitorsCount" in i:
                downMonitorsCount = i['downMonitorsCount']
            else:
                downMonitorsCount = 0
            if "criticalMonitorsCount" in i:
                criticalMonitorsCount = i['criticalMonitorsCount']
            else:
                criticalMonitorsCount = 0
            if "threshold_count" in i:
                threshold_count = i['threshold_count']
            else:
                threshold_count = 0
            if "troubleMonitorsCount" in i:
                troubleMonitorsCount = i['troubleMonitorsCount']
            else:
                troubleMonitorsCount = 0
            self.MONITOR_GRUPS[group_id] = {
                'group_name': group_name,
                'monitors': monitors,
                'status': status,
                'downMonitorsCount': downMonitorsCount,
                'criticalMonitorsCount': criticalMonitorsCount,
                'threshold_count': threshold_count,
                'troubleMonitorsCount': troubleMonitorsCount
            }
        for i in response['data']['monitors']:
            monitor_id = i['monitor_id']
            name = i['name']
            attributeName = i['attributeName']
            monitor_type = i['monitor_type']
            last_polled_time = i['last_polled_time']
            status = i['status']
            if "unit" in i:
                unit = i['unit']
            else:
                unit = None
            if "attribute_key" in i:
                attribute_key = i['attribute_key']
            else:
                attribute_key = None
            if "attribute_label" in i:
                attribute_label = i['attribute_label']
            else:
                attribute_label = None
            if "attribute_value" in i:
                attribute_value = i['attribute_value']
            else:
                attribute_value = None
            self.MONITORS[monitor_id] = {
                'name': name,
                'attributeName': attributeName,
                'monitor_type': monitor_type,
                'last_polled_time': last_polled_time,
                'status': status,
                'unit': unit,
                'attribute_key': attribute_key,
                'attribute_label': attribute_label,
                'attribute_value': attribute_value
            }
    def get_up_monitors(self):
        ''' Get all up monitors from existing monitor groups '''
        up_monitors = []
        for key, values in self.MONITORS.items():
            if values['status'] == 1:
                up_monitors.append(self.MONITORS[key])
        return up_monitors

    def get_msp_customers(self):
        ''' Get all msp customers
            *This function is still in development. '''
        url = '/api/msp/customers'
        response = self.get(url)
        for i in response['data']:
            name = i['name']
            zaaid = i['zaaid']
            self.MSP_CUSTOMERS[name] = zaaid

    def did_refresh(self):
        ''' Check if the token has been refreshed '''
        return self.access_token is not None

    def did_expire(self):
        ''' Raise error if the token has expired '''
        time = datetime.now().timestamp()
        print(f'expires in: {(self.expration_time - time) / 60} minutes')
        if time > self.expration_time:
            raise Exception('Token expired')

    def set_device_key(self):
        ''' Set the device key '''
        self.DEVICE_KEY = self.get_device_key()

    def get_device_key(self):
        ''' Get device key from site24x7 
            *This function is still in development. '''
        url = '/api/device_key'
        response = self.get(url)
        print("get_device_key", response)
        return response['data']['device_key']

if __name__ == '__main__':
    _client_id = "xxx"
    _client_secret = "xxx"
    _code ="xxx"
    zoho = ZohoConnection(_client_id, _client_secret, _code)
    print(zoho.headers)
    zoho.get_current_status_all()
    get = zoho.get('/api/current_status')
    for i in zoho.get_up_monitors():
        print(i['name'], i['status'])
    # zoho.get_msp_customers()
    # for i in zoho.MSP_CUSTOMERS:
    #     print(i, zoho.MSP_CUSTOMERS[i])
    # device_key = zoho.get_device_key()
    # print(device_key)
