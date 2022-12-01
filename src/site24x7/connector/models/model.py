from abc import ABC
from ...utils.util import validatePluginData, guessMetricByType

class ClientModel(ABC):
    '''
        date_created is a [str] in the format of MMM DDDD, YYYY
            example: "Aug 18th, 2022"
        match_list is an optional [list] of strings that are used to match the keys in the dict
            example: ['Fabletics', 'Yitty']
        match_case is an optional [str] that is used to either exact match or case insensitive match the keys in the dict
            default: insensitive match
            example: "exact" or "insensitive"
        ignored_list is an optional [list] of strings that are used to ignore the keys in the dict
            example: ['querytime', 'querytime_ms', 'querytime-ms']
    '''
    def __init__(self, _dict=None, author=None, plugin_version=1, heartbeat_required="true",
    date_created=None, match_list=None, match_case="insensitive", ignored_list=None):
        self.dict = {}
        if not author:
            self.author = "TechStyleOS"
        else:
            self.author = author
        if not ignored_list:
            self.ignored_list = []
        else:
            self.ignored_list = ignored_list
        self.__setitem__('author', self.author)
        self.plugin_version = plugin_version
        self.__setitem__('plugin_version', self.plugin_version)
        self.heartbeat_required = heartbeat_required
        self.__setitem__('heartbeat_required', self.heartbeat_required)
        self.date_created = date_created
        self.__setitem__('date_created', self.date_created)
        if match_list:
            if match_case == "exact" or match_case == "sensitive":
                for key in _dict.keys():
                    for i in match_list:
                        if i.lower() == key.lower():
                            self.__setitem__(key, _dict[key])
            elif match_case == "insensitive":
                for key in _dict.keys():
                    for i in match_list:
                        if i.lower() in key.lower():
                            self.__setitem__(key, _dict[key])
        elif _dict:
            self.dict.update(_dict)
        if len(self.ignored_list) > 0:
            for key in self.ignored_list:
                try:
                    self.__delitem__(key)
                except KeyError:
                    pass
        self.base_values_list = ["total","units","author","plugin_version","heartbeat_required","date_created","querytime"]
        self.validate()

    def __getitem__(self, key):
        return self.dict[key]
    def __setitem__(self, key, value):
        self.dict[key] = value
    def __delitem__(self, key):
        del self.dict[key]
    def __contains__(self, key):
        return key in self.dict
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        return iter(self.dict)
    def __legthcheck__(self, string:str):
        # string limit is 20 on site24x7 plugin dashboard
        if len(string) > 20:
            raise Exception("String length is greater than 20")

    def set_author(self, author:str):
        ''' author is a [str] in the format of "Firstname Lastname" '''
        self.__legthcheck__(author)
        self.author = author
        self.__setitem__('author', self.author)

    def set_plugin_version(self, plugin_version:int):
        ''' plugin_version is a [int] '''
        self.__legthcheck__(plugin_version)
        self.plugin_version = plugin_version
        self.__setitem__('plugin_version', self.plugin_version)

    def set_heartbeat_required(self, heartbeat_required:bool):
        ''' heartbeat_required is a [bool] '''
        self.__legthcheck__(heartbeat_required)
        self.heartbeat_required = heartbeat_required
        self.__setitem__('heartbeat_required', self.heartbeat_required)

    def set_date_created(self, date_created:str):
        ''' date_created is a [str] in the format of MMM DDDD, YYYY'''
        self.__legthcheck__(date_created)
        self.date_created = date_created
        self.__setitem__('date_created', self.date_created)

    def validate(self):
        ''' Validate the model '''
        validatePluginData(self.dict)

    def set_metric_types(self):
        ''' create and set the metric types into main dictionary'''
        self.validate()
        metric_units = guessMetricByType({}, self.dict)
        self.__setitem__('units', metric_units)

    def calculate_total_without_base_values(self) -> str:
        ''' calculate the total of all metrics without base values '''
        total = 0
        for key, value in self.dict.items():
            for i in self.base_values_list:
                if key == i:
                    continue
            else:
                try:
                    total += int(value)
                except ValueError:
                    pass
        self.__setitem__('total', total)
        return total

    def set_unit(self, key, value):
        ''' set the unit for the metric '''
        self.dict['units'][key] = value

    def delete_unit(self, key):
        ''' delete the unit for the metric '''
        del self.dict['units'][key]

    def get_unit(self, key):
        ''' get the unit for the metric '''
        del self.dict['units'][key]

    def check_ignored_list(self, key):
        ''' check if the key is in the ignored list '''
        if key in self.ignored_list:
            return True
        else:
            return False
