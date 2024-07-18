#!/bin/bash

# network_diagnostics.sh

# Function to check DNS resolution
check_dns() {
    echo "Checking DNS resolution..."
    DNS_RESULT=$(nslookup google.com)
    if [[ $? -eq 0 ]]; then
        echo "DNS Check: Pass"
        echo "- Result: $DNS_RESULT"
    else
        echo "DNS Check: Fail"
        echo "- Result: $DNS_RESULT"
    fi
}

# Function to check routing table
check_routing_table() {
    echo "Routing table:"
    netstat -rn
}

# Function to check open ports
check_open_ports() {
    echo "Checking open ports..."
    OPEN_PORTS=$(ss -tuln)
    echo "Open Ports: $OPEN_PORTS"
}

# Function to perform speed test
perform_speed_test() {
    echo "Performing speed test..."
    if command -v speedtest-cli &> /dev/null
    then
        SPEED_TEST_RESULT=$(speedtest-cli --simple)
    else
        echo "speedtest-cli is not installed. Installing now..."
        sudo apt-get install -y speedtest-cli
        SPEED_TEST_RESULT=$(speedtest-cli --simple)
    fi

    DOWNLOAD_SPEED=$(echo "$SPEED_TEST_RESULT" | grep 'Download' | awk '{print $2 " " $3}')
    UPLOAD_SPEED=$(echo "$SPEED_TEST_RESULT" | grep 'Upload' | awk '{print $2 " " $3}')
    if [[ -n "$DOWNLOAD_SPEED" && -n "$UPLOAD_SPEED" ]]; then
        echo "Speed Test: Pass"
        echo "Download Speed: $DOWNLOAD_SPEED"
        echo "Upload Speed: $UPLOAD_SPEED"
    else
        echo "Speed Test: Fail"
        echo "Result: $SPEED_TEST_RESULT"
    fi
}

# Run all checks
check_dns
check_routing_table
check_open_ports
perform_speed_test

echo "Network diagnostics completed."
