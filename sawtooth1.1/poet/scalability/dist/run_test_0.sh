#!/bin/bash

#setup
counter=0
txn_count=10
txn_counter=1
node="http://10.0.0.20:1002"
result_path="/home/manhattan/Desktop/research_testbed/sawtooth1.1/poet/scalability/results/sequential"

#get ip address
IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)
file_name=`echo "$IP"`
cd "$result_path"
touch "$file_name"
image='DSCN0010.jpg'
for i in {1..1000}
do
  echo "#txn: " $txn_counter >> "$file_name"
  echo "transaction sent at: " `date "+%T.%N"`  >> "$file_name"
  nohup python3 /home/manhattan/Desktop/research_testbed/tp/iot_testbed/bin/iot_tp.py send "$image" --path /home/manhattan/Desktop/research_testbed/test_images/ --url "$node" >> "$file_name" &
  let "txn_counter+=1"
done
