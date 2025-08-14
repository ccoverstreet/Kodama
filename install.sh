#!/usr/bin/env bash

sudo cp backend/*.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable kodamaweb kodamavideo kodamacontrol
sudo systemctl start kodamaweb kodamavideo kodamacontrol
