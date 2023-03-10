import json
from datetime import datetime
import requests
AVAILABLE_SCOPES = "Site24x7.Account.Read, Site24x7.Account.Create, Site24x7.Account.Update, Site24x7.Account.Delete, Site24x7.Account.All, Site24x7.Reports.Read, Site24x7.Reports.Create, Site24x7.Reports.Update, Site24x7.Reports.Delete, Site24x7.Reports.All,  Site24x7.Operations.Read, Site24x7.Operations.Create, Site24x7.Operations.Update, Site24x7.Operations.Delete, Site24x7.Operations.All, Site24x7.Msp.Read, Site24x7.Msp.Create, Site24x7.Msp.Update, Site24x7.Msp.Delete, Site24x7.Msp.All, Site24x7.Bu.Read, Site24x7.Bu.Create, Site24x7.Bu.Update, Site24x7.Bu.Delete, Site24x7.Bu.All"
READ_SOPES = "Site24x7.Account.Read, Site24x7.Reports.Read, Site24x7.Operations.Read, Site24x7.Admin.Read"
ALL_SOPES = "Site24x7.Account.All, Site24x7.Reports.All, Site24x7.Operations.All, Site24x7.Admin.All"
current_status_type = [
    'monitor_id',
    'name',
    'monitor_type',
    'status',
]
class ZohoConnection:
    ''' Zoho connection class for Oath2.0 authentication workflow
        :param client_id: Zoho client id
        :param client_secret: Zoho client
        :param code: Zoho authorization code
        :param refresh_token: Zoho refresh token
        :param access_token: Zoho access token
        :param cache: Use cache file, default True, if False will ignore cache file.
            cache will be saved into .cache after each refresh or authorization code function
    '''
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
            self.expration_time_redable = datetime.fromtimestamp(self.expration_time).strftime('%Y-%m-%d %H:%M:%S')
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
            self.expration_time_redable = datetime.fromtimestamp(self.expration_time).strftime('%Y-%m-%d %H:%M:%S')
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
            self.expration_time_redable = datetime.fromtimestamp(self.expration_time).strftime('%Y-%m-%d %H:%M:%S')
            self.headers['Authorization'] = 'Zoho-oauthtoken ' + self.access_token
        else:
            raise Exception('Error refreshing token')
        # save all data to a text file
        self.save_data_into_file()

    def save_data_into_file(self):
        ''' Save all data into a file '''
        with open('.cache', 'w', encoding="utf-8") as cache_file:
            self.timestamp = datetime.now().timestamp()
            self.timestamp_radable = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            cache_file.write(json.dumps(self.__dict__, indent=4))

    def get(self, url, params:dict=None, timeout:int=20) -> dict:
        ''' GET request '''
        self.refresh()
        url = self.api_domain + url
        headers = self.headers
        response = requests.get(url, params=params, headers=headers, timeout=20)
        json_response = json.loads(response.text)
        if response.status_code == 200:
            return json_response
        else:
            code = json_response['code']
            message = json_response['message']
            raise requests.exceptions.HTTPError(f'Error getting response with status {response.status_code}, code: {code}, message: {message}')

    def put(self, url, params:dict=None) -> dict:
        ''' PUT request '''
        self.refresh()
        url = self.api_domain + url
        headers = self.headers
        response = requests.put(url, params=params, headers=headers, timeout=20)
        json_response = json.loads(response.text)
        if response.status_code == 200:
            return json_response
        else:
            code = json_response['code']
            message = json_response['message']
            raise requests.exceptions.HTTPError(f'Error getting response with status {response.status_code}, code: {code}, message: {message}')

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
            self.MONITORS[monitor_id] = {
                'name': name,
                'monitor_type': monitor_type,
                'status': status
            }

    def get_all_monitors(self):
        ''' Get all monitors from site24x7 '''
        url = '/api/monitors'
        response = self.get(url, timeout=60)
        code = response['code']
        message = response['message']
        if message != 'success':
            raise requests.exceptions.HTTPError(f'Error on all monitors with status {response.status_code}, code: {code}, message: {message}')
        for i in response['data']:
            monitor_id = i['monitor_id']
            monitor_type = i['type']
            if 'name' in i:
                name = i['name']
            else:
                name = i['display_name']
            if 'status' in i:
                status = i['status']
            else:
                status = i['state']
            self.MONITORS[monitor_id] = {
                'name': name,
                'monitor_type': monitor_type,
                'status': status,
            }
        return self.MONITORS

    def get_up_monitors(self):
        ''' Get all up monitors from existing monitor groups '''
        up_monitors = []
        for key, values in self.MONITORS.items():
            if values['status'] == 1:
                _dict = self.MONITORS[key]
                _dict.update({"id": key})
                up_monitors.append(_dict)
        return up_monitors

    def get_monitor_by_name(self, name):
        ''' Get monitor by name '''
        for key, values in self.MONITORS.items():
            if values['name'] == name:
                _dict = self.MONITORS[key]
                _dict.update({"id": key})
                return _dict
        return None

    def get_monitors_name_includes(self, name):
        ''' Get monitors by name '''
        monitors = []
        for key, values in self.MONITORS.items():
            if name.lower() in values['name'].lower():
                _dict = self.MONITORS[key]
                _dict.update({"id": key})
                monitors.append(_dict)
        return monitors

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
        experition_time = (self.expration_time - time) / 60
        if experition_time < 5:
            print(f'Access expires in: {experition_time} minutes')
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

    def poll_monitor(self, monitor_id):
        ''' Poll a monitor. Initializes polling and returns the status of polling '''
        url = f'/api/monitor/poll_now/{monitor_id}'
        response = self.get(url)
        return response['data']['status']

    def poll_status(self, monitor_id):
        ''' Get the status of polling '''
        url = f'/api/monitor/status_poll_now/{monitor_id}'
        response = self.get(url)
        return response['data']['status']

    def activate_monitor(self, monitor_id):
        ''' Activate a monitor '''
        url = f'/api/monitors/activate/{monitor_id}'
        response = self.put(url)
        return response['message']
    
    def suspend_monitor(self, monitor_id):
        ''' Suspend a monitor '''
        url = f'/api/monitors/suspend/{monitor_id}'
        response = self.put(url)
        return response['message']
    
    def get_monitor_count(self):
        ''' Get the number of monitors from site24x7 '''
        url = f"/api/monitors/status/count"
        response = self.get(url)
        if response['message'] == "success":
            data = response['data']
            down_count = data['down']['count']
            up_count = data['up']['count']
            critical_count = data['critical']['count']
            trouble_count = data['trouble']['count']
            suspended_count = data['suspended']['count']
            maintenance_count = data['maintenance']['count']
            discovery_count = data['discovery']['count']
            total_count = data['total']['count']
            print("####################")
            print(f"Total: {total_count}")
            print(f"Up: {up_count}")
            print(f"Down: {down_count}")
            print(f"Critical: {critical_count}")
            print(f"Trouble: {trouble_count}")
            print(f"Suspended: {suspended_count}")
            print("####################")
            return data
        else:
            return None

    def suspend_given_plugin_name_list(self, name_list:list):
        ''' Suspend a list of monitors '''
        for i in name_list:
            monitor = self.get_monitor_by_name(i)
            if not monitor:
                print(f"Monitor {i} not found")
                continue
            self.suspend_monitor(monitor['id'])
            print(f"Suspended {i['name']}")

    def activate_given_plugin_name_list(self, name_list:list):
        ''' Activate a list of monitors '''
        for i in name_list:
            monitor = self.get_monitor_by_name(i)
            if not monitor:
                print(f"Monitor {i} not found")
                continue
            self.activate_monitor(monitor['id'])
            print(f"Suspended {i['name']}")
