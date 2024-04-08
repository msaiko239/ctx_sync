#!/bin/sh
set -x

pip3 install flask
pip3 install pycurl

touch /var/log/ctx_sync.log

cp -fr ctx_sync.py /opt/
cp -fr logger_app.py /opt/
cp -fr ctx_sync.service /etc/systemd/system/

chmod 644 /etc/systemd/system/ctx_sync.service
sudo systemctl daemon-reload
sudo systemctl enable ctx_sync.service
sudo systemctl start ctx_sync.service
