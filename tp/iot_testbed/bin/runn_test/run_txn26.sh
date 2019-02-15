#!/bin/bash
#validate parms
while getopts "hs:t:" arg; do
    case $arg in
        h)
            echo "-r <rate to send transactions>"
            echo "-c <how many transaction"
            echo "example: -s 2 -c 5 <every two seconds sen 5 txn>"
            exit
            ;;
        s)
            rate=$OPTARG
            echo "Setting rate to:" $rate
            ;;
        t)
            txn_count=$OPTARG
            echo "Setting count to:" $txn_count
            ;;
  esac
done

#assign default values
if [ -z "$rate" ]
    then
        rate=2
fi

if [ -z "$txn_count" ]
    then
        txn_count=1
fi

echo "Rate: " $rate
echo "# Transactions: " $txn_count

#go to images folder
cd /home/manhattan/Documents/research-paper/results
#start sending transactions
send_count=0
#get ip address
IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)
file_name=`echo "$IP"`
touch "$file_name"
echo "Client $IP started at: " `date` >> "$file_name"
cd /home/manhattan/Documents/research-paper/images
while true
do
    for (( c=1; c<=$txn_count; c++ ))
        do
            #pick random image and process transaction
            image=`ls * | shuf -n 1`
            echo "python3 /home/manhattan/Documents/research-paper/iot_testbed/bin/iot_tp.py send $image"
            python3 /home/manhattan/Documents/research-paper/iot_testbed/bin/iot_tp.py send "$image" --path /home/manhattan/Documents/research-paper/images/ --url http://10.0.0.26:1002
            let "send_count+=1"
            #send 10 images and then stop
            if [ $send_count -eq 10 ]
              then
                echo "10 images sent"
                cd /home/manhattan/Documents/research-paper/results
                echo "Client $IP stopted at: " `date` >> "$file_name"
                exit
            fi

            #move the image to an archive folder, avoid duplicates txn
            #mv "$image" /home/"$USER"/Desktop/testbed/iot_tp/archive
            #check if we still images to process
            # image_count=`ls | wc -l`
            # if [ "$image_count" -eq 0  ]
            #     then
            #         echo "No more images"
            #         exit
            # fi
    done
    sleep $rate
done
