#!/usr/bin/env python3
import os
import ezodf
import yaml
import json
import datetime
from optparse import OptionParser
from components.grovepi import *
from components.netio import *
from components.influxdb_rw import *

os.chdir('/home/pi/scripts/grow/v2/')
parser = OptionParser()
parser.add_option("--stage", dest="stage")
parser.add_option("--humidity", default=0, dest="hum_limit")
parser.add_option("--temperature", default=0, dest="temp_limit")
(options, args) = parser.parse_args()


def read_config(file):
    with open('config.yml') as f:
        yaml_read = yaml.safe_load(f)
    return yaml_read


def read_ods(file):
    doc = ezodf.opendoc(file)
    p = doc.sheets['SEQ']
    config_map = {'SED': [f"{p['H2'].value}-{p['I2'].value}",
                          f"{p['H3'].value}-{p['I3'].value}",
                          f"{p['H4'].value}-{p['I4'].value}",
                          f"{p['H5'].value}-{p['I5'].value}"],
                  'VEG': [f"{p['J2'].value}-{p['K2'].value}",
                          f"{p['J3'].value}-{p['K3'].value}",
                          f"{p['J4'].value}-{p['K4'].value}",
                          f"{p['J5'].value}-{p['K5'].value}"],
                  'FLO': [f"{p['L2'].value}-{p['M2'].value}",
                          f"{p['L3'].value}-{p['M3'].value}",
                          f"{p['L4'].value}-{p['M4'].value}",
                          f"{p['L5'].value}-{p['M5'].value}"],
                  'FLU': [f"{p['N2'].value}-{p['O2'].value}",
                          f"{p['N3'].value}-{p['O3'].value}",
                          f"{p['N4'].value}-{p['O4'].value}",
                          f"{p['N5'].value}-{p['O5'].value}"],
                  'DRY': [f"{p['P2'].value}-{p['Q2'].value}",
                          f"{p['P3'].value}-{p['Q3'].value}",
                          f"{p['P4'].value}-{p['Q4'].value}",
                          f"{p['P5'].value}-{p['Q5'].value}"]}
    return config_map


def avg(list_in):
    hum, temp = [], []
    for i in list_in:
        for n in i:
            if n['measurement'] == 'humidity' and n['tags']['sensor'] in range(1, 5):
                hum.append(n['fields']['value'])
            if n['measurement'] == 'temperature' and n['tags']['sensor'] in range(1, 5):
                temp.append(n['fields']['value'])
    return sum(hum)/4, sum(temp)/4


TIME_STAMP = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# Read config yml
CONFIG_READ = read_config('config.yml')

# Read ods scheduller
ODS_READ = read_ods(f"../growdiary/{CONFIG_READ['growdiary']}")

# Read sensors values
grovepi = Sensors(TIME_STAMP)
sensors_values = grovepi.get_sensors_values()
sensors_sum_avg = avg(sensors_values)

# Netio json api tx
netio = Netio(ODS_READ, options.stage, int(options.hum_limit), int(options.temp_limit))
netio_state = netio.switch(CONFIG_READ['netio'][0]['url'],
                           CONFIG_READ['netio'][1]['user'],
                           CONFIG_READ['netio'][2]['password'],
                           sensors_sum_avg[0], sensors_sum_avg[1])

# self, influxdb_ip, influxdb_port, influxdb_user, influxdb_pass, influxdb_db, timestamp
influxdb = Influxdb(CONFIG_READ['influxdb'][0]['user'],
                    CONFIG_READ['influxdb'][1]['password'],
                    CONFIG_READ['influxdb'][2]['db_name'],
                    CONFIG_READ['influxdb'][3]['url'],
                    CONFIG_READ['influxdb'][4]['port'],
                    TIME_STAMP)
# netio influxdb tx
netio_state_pars = influxdb.dump_netio_state(json.loads(netio_state), TIME_STAMP)
netio_to_influx = influxdb.tx(netio_state_pars)

# grovepi sensors influxdb tx
grovepi_to_influx = influxdb.tx(sensors_values)
