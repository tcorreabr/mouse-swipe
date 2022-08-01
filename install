#! /usr/bin/env bash

cd src && mkdir /usr/local/share/mouse-swipe && cp config.py swipe_button.py main.py mouse.py virtual_device.py /usr/local/share/mouse-swipe
cd ../data && cp mouse-swipe.service /etc/systemd/system && cp -n mouse-swipe.conf /etc
systemctl daemon-reload
systemctl enable mouse-swipe.service --now