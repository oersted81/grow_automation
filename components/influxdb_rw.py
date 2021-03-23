#!/usr/bin/env python3
from influxdb import InfluxDBClient


class Influxdb:

    def __init__(self, influxdb_user, influxdb_pass, influxdb_db, influxdb_ip, influxdb_port, timestamp):
        self.influxdb_ip = influxdb_ip
        self.influxdb_port = influxdb_port
        self.influxdb_user = influxdb_user
        self.influxdb_pass = influxdb_pass
        self.influxdb_db = influxdb_db
        self.timestamp = timestamp

    def dump_netio_state(self, status, timestamp):
        self.out = []
        for i in status['Outputs']:
            _json_body = [
                {
                    "measurement": "netio_status",
                    "tags": {
                        "output": i['Name'],
                    },
                    "time": timestamp,
                    "fields": {
                        "value": int(i['State'])
                    }
                }
            ]
            self.out.append(_json_body)
        return self.out

    def tx(self, ary_json_in):
        # host, port, user, password, dbname
        client = InfluxDBClient(self.influxdb_ip, self.influxdb_port, self.influxdb_user,
                                self.influxdb_pass, self.influxdb_db)
        client.create_database(self.influxdb_db)
        client.switch_database(self.influxdb_db)
        for i in ary_json_in:
            client.write_points(i, time_precision='ms')
