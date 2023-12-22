#references/credits: https://www.bentasker.co.uk/posts/blog/house-stuff/how-much-more-energy-efficient-is-eco-mode-on-a-dish-washer.html#tapo
#updated library to query https://github.com/almottier/TapoP100/tree/main

import os
import influxdb_client
from PyP100 import PyP110
from influxdb_client.client.write_api import SYNCHRONOUS

user = "email"
passw = "pass"


plugs = [
    {"name": "x", "ip": "1.2.3.4"},
]

bucket = "energy"
org = ""

def sendToInflux(name, watts, today_w):
    ''' Take the values and send into Influx

    Unlike kasa plugs, usage is reported in Wh not kWh
    '''
    print("Sending value")

    # Set up to send into Influx
    client = influxdb_client.InfluxDBClient(
        url="http://127.0.0.1:8086",
        token="",
        org=""
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)
    try:
        p = influxdb_client.Point("power_watts").tag("host", name).field("consumption", float(watts))
        write_api.write(bucket=bucket, org=org, record=p)
    except:
        print("Error submitting locally")

    if today_w:
        p = influxdb_client.Point("power_watts").tag("host", name).field("watts_today", int(float(today_w)))
        write_api.write(bucket=bucket, org=org, record=p)

# Iterate over the configured plugs
for plug in plugs:
    try:
        p110 = PyP110.P110(plug["ip"], user, passw)
        p110.login() #Sends credentials to the plug and creates AES Key and IV for further methods
        usage_dict = p110.getEnergyUsage()
    except:
        print("Failed to communicate with device {}".format(plug["ip"]))
        continue

    today_usage = usage_dict.get('today_energy') / 1000
    now_usage_w = usage_dict.get('current_power') / 1000

    #print("Plug: {} using {}W, today: {} kWh".format(plug["name"],
    #                                                now_usage_w,
    #                                                today_usage/1000))

    sendToInflux(plug["name"], now_usage_w, today_usage)
    del(p110) # Tidy away the var
