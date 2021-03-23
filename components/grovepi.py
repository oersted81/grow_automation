#!/usr/bin/env python3

import grovepi
import math


class Sensors:

    def __init__(self, timestamp):
        self.timestamp = timestamp

    def dump_temperature(self, temp, sensor):
        self.json_body = [
            {
                "measurement": 'temperature',
                "tags": {
                    "sensor": sensor,
                },
                "time": self.timestamp,
                "fields": {
                    "value": temp
                }
            }
        ]
        return self.json_body

    def dump_humidity(self, hum, sensor):
        self.json_body = [
            {
                "measurement": 'humidity',
                "tags": {
                    "sensor": sensor,
                },
                "time": self.timestamp,
                "fields": {
                    "value": hum
                }
            }
        ]
        return self.json_body

    def dump_moisture(self, mois):
        self.json_body = [
            {
                "measurement": 'soil_moisture',
                "tags": {
                    "sensor": 0,
                },
                "time": self.timestamp,
                "fields": {
                    "value": mois
                }
            }
        ]
        return self.json_body

    def get_sensors_values(self):
        try:
            _output_values = [self.dump_moisture(int(grovepi.analogRead(16)))]
            for i in range(2, 7):
                sensor_no = i - 1
                [temp, hum] = grovepi.dht(i, 0)
                if not math.isnan(temp) and not math.isnan(hum):
                    _output_values.append(self.dump_temperature(float(temp), sensor_no))
                    _output_values.append(self.dump_humidity(float(hum), sensor_no))
        except IOError:
            pass

        return _output_values
