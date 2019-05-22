#get ip address
IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)

#create folders
mkdir data
mkdir logs
mkdir keys
export SAWTOOTH_HOME=`pwd`

#create peer keys
sawadm keygen
sawtooth keygen

#validator
#sawtooth-validator -vv --bind component:tcp://127.0.0.1:1001 --bind network:tcp://$IP:1003 --endpoint tcp://$IP:1003 --bind consensus:tcp://127.0.0.1:5050 --peers tcp://10.0.0.20:1003,tcp://10.0.1.21:1003 &
#sawtooth-validator -vvv --bind component:tcp://127.0.0.1:1001 --bind network:tcp://$IP:1003 --endpoint tcp://$IP:1003 --bind consensus:tcp://127.0.0.1:5050 --peering dynamic --seeds tcp://10.0.0.20:1003,tcp://10.0.5.20:1003,tcp://10.0.11.20:1003 --scheduler parallel &
#sawtooth-validator -vvv --bind component:tcp://127.0.0.1:1001 --bind network:tcp://$IP:1003 --endpoint tcp://$IP:1003 --bind consensus:tcp://127.0.0.1:5050 --peering dynamic --seeds tcp://10.0.2.20:1003 --scheduler parallel &
sawtooth-validator -vvv --bind component:tcp://127.0.0.1:1001 --bind network:tcp://$IP:1003 --endpoint tcp://$IP:1003 --bind consensus:tcp://127.0.0.1:5050 --peering dynamic --seeds tcp://10.0.0.20:1003,tcp://10.0.5.20:1003,tcp://10.0.11.20:1003 --scheduler serial &

#rest api
sawtooth-rest-api -v --bind $IP:1002 --connect 127.0.0.1:1001 &

#processors
settings-tp -v --connect tcp://127.0.0.1:1001 &
poet-validator-registry-tp --connect tcp://127.0.0.1:1001 &
intkey-tp-python -v --connect tcp://127.0.0.1:1001 &
python3 /home/manhattan/Desktop/research_testbed/tp/iot_testbed/bin/iot-tp -v --connect tcp://127.0.0.1:1001 &

#engine
poet-engine -vv --connect tcp://127.0.0.1:5050 --component tcp://127.0.0.1:1001 &
