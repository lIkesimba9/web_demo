#!/bin/bash
nohup openvpn --config /config/credentials.ovpn > vpn.log &
python3 main.py