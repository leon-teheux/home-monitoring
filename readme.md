# Home monitoring collection

This project contains various scripts that can be used to get information from Remeha Calenta boilers, Youless (both electricity and gas) and FritzBox routers. This information is then stored in a local Influx database. This can then be displayed using a tool such as Grafana.

## Getting Started

These scripts are self-sufficient and are proven to work fine on a Raspberry Pi3 running Rasbian. The scripts are mostly modified existing projects (see Acknowledgments) to enable InfluxDB integration.

### Prerequisites

* Generic: Up to date Rasberry Pi Rasbian image with InfluxDB installed. Databases need to be configured and listening on UDP sockets as per code.
* Youless: IP connectivity to the Youless itself.
* FritzBox: Refer to https://github.com/yunity/fritzinfluxdb. Don't forget to create an user on the FritzBox and make sure the FritzBox is allowing access to read info (UPNP stats etc) and install fritzconnection on your Raspberry Pi.
* Remeha Calenta: Working USB to Serial adapter. Doublecheck its ID in Linux to make sure it's the same as in the script. Refer to https://github.com/fabienroyer/enphase-envoy/ .

### Installing

Copy the files to your Raspberry and have them execute regularly. For example, add the following to your crontab to execute them directly:
@reboot python /home/pi/youless-gas.py &
@reboot python /home/pi/youless-stroom.py &
@reboot sleep && python /home/pi/remeha.py &


Or with a launcher script:
@reboot sh /etc/launcher.sh &

Example launcher.sh (don't forget to make it executable!):
#!/bin/sh
while true
do
lua /home/pi/enphase.lua
sleep 5
done


## License

This project is licensed under the MIT License - see the [license.md](license.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* https://github.com/yunity/fritzinfluxdb
* https://github.com/fabienroyer/enphase-envoy/

