#!/bin/bash

check_sentinel_installed() {
    if [ -d /Applications/SentinelOne/ ]; then
        echo "Already Installed"
        exit 0
    fi
}

create_directory_if_not_exists() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    fi
}

#Install S1 if Package and Group Token already Exsists Locally
install_sentinel_from_local() {
    local pkg_path="/Users/%LastConsoleUser%/Public/IT/SentinelOne/SentinelOne.pkg"
    local token_path="/Users/%LastConsoleUser%/Public/IT/SentinelOne/com.sentinelone.registration-token"

    if [ -f "$pkg_path" ] && [ -f "$token_path" ]; then
        sudo /usr/sbin/installer -allowUntrusted -pkg "$pkg_path" -target /
        if [ -d /Applications/SentinelOne/ ]; then
            echo "Install Complete"
            exit 0
        else
            echo "Install incomplete"
            exit 1
        fi
    fi
}

fetch_sentinel_token() {
    #If you have a Serverless Function to Fetch Group Token Dynamically
    #Uncomment the follwing code and delete line 49, Uncomment Function Call in Main

    #local API_URL="{ENV:API_URL}" Replace with Url To fetch Group Token
    #local HEADER_CONTENT_TYPE="Content-Type: application/json"
    #local HEADER_AUTHORIZATION="x-api-key: "

    
    #echo "Fetching Sentinel Token..."
    #api_response=$(curl -X GET -H "$HEADER_CONTENT_TYPE" -H "$HEADER_AUTHORIZATION" "$API_URL")
    #sentinelToken=$(echo "$api_response" | grep -o "\"groupToken\": *\"[^\"]*\"" | awk -F'\"' '{print $4}')

    #echo "$sentinelToken" > "/Users/%LastConsoleUser%/Public/IT/SentinelOne/com.sentinelone.registration-token"
    echo "{{ENV:SToken}}" > "/Users/%LastConsoleUser%/Public/IT/SentinelOne/com.sentinelone.registration-token"
}

#If you have Instructions for remediation you want on User's machines, please uncomment and place the link in the instrucitionsDownloadLink Var

#fetch_instructions(){
#    local instrucitionsDownloadLink="{ENV:InstructionsLink}"
#    local file_path"=/Users/%LastConsoleUser%/Public/IT/SentinelOne/SentinelOne\ offline\ install.pdf"
#    if [ ! -d "$file_path" ]; then
#        curl -s -L -o /Users/%LastConsoleUser%/Public/IT/SentinelOne/SentinelOne\ offline\ install.pdf $instrucitionsDownloadLink
#    fi
#}


download_sentinel_pkg() {
    local downloadLink="{ENV:S1PackageDownload}" #Replace with Download Link of SentinelOne Package
    local pkgName="SentinelOne.pkg"
    local pkg_dir="/Users/%LastConsoleUser%/Public/IT/SentinelOne/"
    local file_path="/Users/%LastConsoleUser%/Public/IT/SentinelOne/$pkgName"

    create_directory_if_not_exists "$pkg_dir"

    # Download Agent
    for attempt in {1..3}; do
        echo "Attempting to download (Attempt $attempt)..."
        if [ ! -e "$file_path" ]; then
            curl -s -L -o "$pkg_dir/$pkgName" "$downloadLink" && echo "Downloaded"
            if [ $? -ne 0 ]; then
                echo "Download failed. Retrying..."
                continue
            fi
        fi

        downloaded_checksum="$(shasum "$file_path" | awk '{print $1}')"
        echo "Downloaded Checksum: $downloaded_checksum"
        expected_shasum="xx" #Replace with shasum of S1 Package
        if [ "$downloaded_checksum" != "$expected_shasum" ]; then
            echo "Checksum mismatch. Retrying..."
        else
            echo "Checksum Matches"
            break
        fi

        if [ $attempt -lt 3 ]; then
            echo "Retrying..."
        else
            echo "Exceeded maximum number of attempts. Aborting installation."
            exit 1
        fi
    done

    # Proceed with installation
    sudo /usr/sbin/installer -allowUntrusted -pkg "$file_path" -target /
}

main() {
    #fetch_instructions
    check_sentinel_installed
    install_sentinel_from_local
    fetch_sentinel_token
    download_sentinel_pkg
}

main
