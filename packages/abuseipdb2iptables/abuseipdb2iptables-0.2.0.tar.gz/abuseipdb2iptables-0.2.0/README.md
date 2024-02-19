# abuseipdb2iptables [![Python application](https://github.com/iroco-co/abuseipdb2iptables/actions/workflows/python-app.yml/badge.svg)](https://github.com/iroco-co/abuseipdb2iptables/actions/workflows/python-app.yml)

Small python utility to convert abuseipdb json file into iptables rules.

## Install

With pip : 
```shell
pip install abuseipdb2iptables
```

## Usage

It will group similar ip addresses with networks CIDR.

```shell
abuseipdb2iptables path/to/abuseipdb.json
-A INPUT -s 192.168.1.12/32 -j DROP
-A INPUT -s 172.16.0.0/31 -j DROP
-A INPUT -s 10.9.8.7/31 -j DROP
...
```
