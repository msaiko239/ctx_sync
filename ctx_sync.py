#!/usr/bin/env python3
from flask import Flask, request, abort
import json
import urllib3
import pycurl
import io
import getpass
from urllib.parse import urlencode
import logger_app
from logger_app import get_logger
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EPC1 = "192.168.88.32"
EPC2 = "192.168.88.56"
APIUSER = "sysadmin"
APIPASS = "password"

app = Flask(__name__)

app_logger = get_logger()

print ("****This application is a proof of concept and is not support by Druid Software****")

def process_detach(imsi, ep_address):
    #app_logger = get_logger()
    app_logger.info(f"Attach request for {imsi} in {ep_address}")
    url =str("https://%s:%s@%s/api/subscriber?imsi=%s" % (APIUSER, APIPASS, ep_address, imsi))
    try:
        buffer = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.USERNAME, APIUSER)
        c.setopt(pycurl.PASSWORD, APIPASS)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(pycurl.CONNECTTIMEOUT, 10)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        status_code = c.getinfo(pycurl.RESPONSE_CODE)
        c.close()
        if status_code == 200:
            data = json.loads(buffer.getvalue().decode('utf-8'))
            for item in data:
                app_logger.info(f"Subscriber {imsi} status in {ep_address} = {item['local_ps_attachment']}")
                if item['local_ps_attachment'] == "ATTACHED":
                    app_logger.info(f"Detaching subscriber {imsi} from {ep_address}")
                    url_imsi =str("https://%s:%s@%s/api/subscriber?imsi=%s" % (APIUSER, APIPASS, ep_address, imsi))
                    patch_data = {"local_ps_attachment": "DETACHED"}
                    postfields = urlencode(patch_data)
                    c = pycurl.Curl()
                    c.setopt(pycurl.URL, url_imsi)
                    c.setopt(pycurl.CUSTOMREQUEST, "PATCH")
                    c.setopt(pycurl.USERNAME, APIUSER)
                    c.setopt(pycurl.PASSWORD, APIPASS)
                    c.setopt(pycurl.SSL_VERIFYPEER, 0)
                    c.setopt(pycurl.SSL_VERIFYHOST, 0)
                    c.setopt(pycurl.CONNECTTIMEOUT, 10)
                    c.setopt(pycurl.POSTFIELDS, postfields)
                    c.perform()
                    status_code = c.getinfo(pycurl.RESPONSE_CODE)
                    if status_code == 200:
                        app_logger.info(f"Subscriber {imsi} detached from {ep_address}")
                    else:
                        app_logger.info(f"Unable to detach subscriber {imsi} from {ep_address}")
                else:
                    app_logger.info(f"{imsi} already detached in {ep_address}")
        else:
            app_logger.info(f"Failed to fetch data. Status code: {status_code}")
    except pycurl.error as e:
        app_logger.info(f"Failed to get object: {e}")
        sys.exit(1)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        app_logger.info(f"Incoming POST from {request.remote_addr}")
        if request.remote_addr == EPC2:
            imsi = request.form.get('imsi')
            if imsi is not None:
                process_detach(imsi, EPC1)
            else:
                app_logger.info(f"Subscriber {imsi} not found in {EPC1}")
        elif request.remote_addr == EPC1:
            imsi = request.form.get('imsi')
            if imsi is not None:
                process_detach(imsi, EPC2)
            else:
                app_logger.info(f"Subscriber {imsi} not found in {EPC2}")
        else:
            app_logger.info(f"POST request from unknown server or does not match subscriber event {request.remote_addr}")
        return '', 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0')


