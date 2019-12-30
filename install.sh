#!/bin/bash

cp lcd.service  /lib/systemd/system/
chmod 644 /lib/systemd/system/lcd.service

sudo systemctl daemon-reload
sudo systemctl enable lcd.service
