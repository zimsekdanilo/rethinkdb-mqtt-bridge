# RethinkDB MQTT bridge
This project contains documentation and implementation of MQTT bridge for refhinkDB in python.
It subscribes to all topics on mqtt broker and saves the data to the database.

The brridge requires connection to MQTT broker and rethinkDB database, installation of those components is described in [Requirements](#Requirements).
## installation
```
git clone https://github.com/zimsekdanilo/rethinkdb-mqtt-bridge.git
```
### Initialization of the database and tables
`python3 MQTTbridge/bridge.py --setup`

#### Run the bridge
`python3 MQTTbridge/bridge.py`

***

## Requirements

### MQTT broker and clients for testing

```
sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
sudo apt-get update
sudo apt-get install mosquitto
sudo apt-get install mosquitto-clients
```

Configure MQTT broker
```
sudo service stop mosquitto
```

edit `/etc/mosquitto/mosquitto.conf` to set username, password. Sample config:
```
pid_file /var/run/mosquitto.pid

persistence true
persistence_location /var/lib/mosquitto/

log_dest file /var/log/mosquitto/mosquitto.log

password_file /etc/mosquitto/passwd
allow_anonymous false
```

Create `/etc/mosquitto/passwd` with desired username and password as in example:
```
myuser:mypass
```
Now encrypt the passwords in the `passwd` file
```
mosquitto_passwd -U passwordfile
```
Start the broker
```
sudo service start mosquitto
```

#### Adding users

`sudo mosquitto_passwd -b /etc/mosquitto/passwd newuser newpassword`

#### Testing the broker
Subscribe to topoc `test` on broker
```
mosquitto_sub -h localhost -t test -u myuser -P mypass
```
In another terminal publish message to topic `test`
```
mosquitto_pub -h localhost -t test -m "835" -u mypass -P mypass
```
If everythink is ok, message is displayed in terminal with subscription.

***
### RethinkDB database
Install the server
```
source /etc/lsb-release && echo "deb http://download.rethinkdb.com/apt $DISTRIB_CODENAME main" | sudo tee /etc/apt/sources.list.d/rethinkdb.list
wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install rethinkdb
```
Run the server
```
rethinkdb
```
