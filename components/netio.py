#!/usr/bin/env python3

import json
import requests
import datetime
from requests.auth import HTTPBasicAuth


class Netio:

    def __init__(self, map, stage, hum_limit, temp_limit):
        self.map = map
        self.stage = stage
        self.hum_limit = hum_limit
        self.temp_limit = temp_limit

    def time_in_range(self, start, end, x):
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end

    def scheduled_time(self):
        _A_OUT = {"Outputs": []}
        _timestamp = datetime.datetime.now().strftime('%H:%M')
        _index = 0

        for key in self.map:
            if key == self.stage:
                for i in self.map[key]:
                    _index += 1
                    parse_map = i.split('-')
                    if parse_map[0] == 'on':
                        _A_OUT["Outputs"].append({"ID": _index, "Action": 1})
                    elif parse_map[0] == 'off':
                        _A_OUT["Outputs"].append({"ID": _index, "Action": 0})
                    else:
                        parse_time = _timestamp.split(':')
                        start = datetime.time(int(parse_map[0].split(':')[0]),
                                              int(parse_map[0].split(':')[1]), 0)
                        end = datetime.time(int(parse_map[1].split(':')[0]),
                                            int(parse_map[1].split(':')[1]), 0)
                        if self.time_in_range(start, end, datetime.time(int(parse_time[0]),
                                                                        int(parse_time[1]), 0)):
                            _A_OUT["Outputs"].append({"ID": _index, "Action": 1})
                        else:
                            _A_OUT["Outputs"].append({"ID": _index, "Action": 0})
        return _A_OUT

    def switch(self, url, user, passwd, hum, temp):
        _response = requests.get(url, auth=HTTPBasicAuth(user, passwd))
        _data = self.scheduled_time()

        if self.hum_limit != 0 and (self.stage in ['SED', 'VEG']):
            if hum <= self.hum_limit:
                _data['Outputs'][3]['Action'] = 1
            elif hum > self.hum_limit:
                _data['Outputs'][3]['Action'] = 0

        if self.hum_limit != 0 and (self.stage in ['FLO', 'FLU']):
            if hum >= self.hum_limit:
                _data['Outputs'][3]['Action'] = 1
            elif hum < self.hum_limit:
                _data['Outputs'][3]['Action'] = 0

        if self.temp_limit != 0:
            if temp >= self.temp_limit:
                _data['Outputs'][1]['Action'] = 1
            elif temp < self.temp_limit:
                _data['Outputs'][1]['Action'] = 0

        if _response.status_code == 200:
            requests.post(f"{url}/netio.json", data=json.dumps(_data),
                          auth=HTTPBasicAuth(user, passwd))

        else:
            pass
        state = requests.get(f"{url}/netio.json", auth=HTTPBasicAuth(user, passwd))
        return state.text
