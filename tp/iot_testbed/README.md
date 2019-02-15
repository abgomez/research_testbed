# Description.
Custom Transaction Processor (TP) to transmit Images metadata, the TP was developed for the Hyperledger Sawtooth Platform.

# How to Use.
Clone the TP code into your desktop:\
`cd ~/Desktop` \
`git clone https://github.com/abgomez/iot_testbed.git` \
`cd ~/Desktop/iot_tp/bin` \
## Prerequisites.
A sawtooth instance running. This guide does not include how to start sawtooth. Documentation regarding sawtooth installation can be found at [Sawtooth Documentation](https://sawtooth.hyperledger.org/docs/core/releases/latest/contents.html).
The TP expects a to find all images in the folder `~/Desktop/iot_tp/images/`, images must be in format jpg
## Start Processor.
Start Processor:
`python3 iot-tp -v`

## Run tests.
To test the TP you can use the script "run_txn.sh", this script submit a certain number of transactions in a constant rate.
The script accept two arguments, time frame to send transactions and number of transaction. The default of these parameters are 2 and 1 respectively.
### Run default.
`cd ~/Desktop/iot_tp/bin`\
`./run_txn.sh`
### run_txn.sh help
`-r <rate to send transactions>
-t <how many transaction>
`
### Example
`./run_txn.sh -s 2 -c 5 <every two seconds sen 5 transactions>`
