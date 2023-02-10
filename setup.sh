#! /usr/bin/env bash

if [ ! -d "resources" ]; then
    mkdir resources
fi

if [ ! -f ".env" ]; then
    echo "Creating an example .env file"
    cat >> .env <<EOF
# provide the values here to be used in the program entrypoint __main__.py
WEBHOOK_EXAMPLE_1="..."
FEED_URL_EXAMPLE_1="..."
WEBHOOK_EXAMPLE_2="..."
FEED_URL_EXAMPLE_2="..."
EOF
else
    echo ".env file already detected, skipping .env example file creation"
fi

if [ ! -d "venv" ]; then
    echo "Creating and setting up virtual environment"

    python3 -m virtualenv venv 2> /dev/null

    if [ $? -ne 0 ]; then
        echo "virtualenv module returned an error code, automatic installation is cancelled."
        echo "Make sure virtualenv module is installed, if not, you can use another module for example 'python3 -m venv venv' to setup a virtual environment or simply install virtualenv with 'python3 -m pip install virtualenv'"
        echo "If venv directory was correctly initialized, just install the requirements manually."
        exit 1
    fi

    source venv/bin/activate
    python3 -m pip install -r requirements.txt 2> /dev/null

    if [ $? -ne 0 ]; then
        echo "pip module returned an error when trying to install the requirements"
        exit 1
    fi
else
    echo "A venv directory is already detected, skipping packages installation"
fi
    
echo -e "\nAll done\nPlease finish the configuration by placing "$(pwd)" in the __main__.py file and placing the env variables in .env"