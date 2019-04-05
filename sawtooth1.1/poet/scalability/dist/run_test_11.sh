#!/bin/bash

#setup
counter=0
txn_count=10
txn_counter=1
node="http://10.0.11.20:1002"
result_path="/home/manhattan/Desktop/research_testbed/sawtooth1.1/poet/scalability/results/1-min/10-nodes/dist/8000/sequential"

#get ip address
IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)
file_name=`echo "$IP"`
cd "$result_path"
touch "$file_name"
image='DSCN0010.jpg'
while true
do
  #start sending transactions
    for (( c=1; c<=$txn_count; c++ ))
        do
          echo "-----------------------------------------------------------------------------------------"
          echo "#txn: " $txn_counter >> "$file_name"
          echo "transaction sent at: " `date`  >> "$file_name"
          python3 /home/manhattan/Desktop/research_testbed/tp/iot_testbed/bin/iot_tp.py send "$image" --path /home/manhattan/Desktop/research_testbed/sawtooth1.1/poet/scalability/images/ --url "$node" >> "$file_name"
          let "txn_counter+=1"
    done

    let "counter+=1"
    if [ $counter -eq 80 ]
      then
        echo "Last transaction  sent at: " `date` >> "$file_name"
        exit
    fi
    sleep 15 #every second
done
