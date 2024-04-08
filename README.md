# ctx_sync
Clone the repo into /tmp/

`git clone https://github.com/msaiko239/ctx_sync`

`cd ctx_sync`

make the install script executable

`chmod a+x install.sh`

run the install script

`./install.sh`

# USing the application
You need to edit the main python file to match the ip addresses of your system.

`vim /opt/ctx_sync.py`

Change the vaules of lines 12, 13, 14 and 15

`EPC1 = <ipaddress>`

`EPC2 = <ipaddress>`

`APIUSER = <username>`

`APIPASS = <password>`


Then restart the service

`systemctl restart ctx_sync`
