#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FIRST_ARG="$1"

run_command() {
    docker-compose -f "$SCRIPT_DIR/../envs/dev/docker-compose.yml" down
    docker volume rm dev_fast_it_database_dev
    docker volume rm mongo_data_logs
    if [ -z "$FIRST_ARG" ]; then
        docker-compose -f "$SCRIPT_DIR/../envs/dev/docker-compose.yml" up --build
    else
        docker-compose -f "$SCRIPT_DIR/../envs/dev/docker-compose.yml" up --build --attach $FIRST_ARG
    fi
}

echo "Launching the script. After it starts, to restart and clear memory, press Ctrl-C."
while true; do
    run_command

    if [ $? -eq 130 ]; then
        echo "Application interrupted. Restarting in 3 seconds. Press Ctrl-C again to cancel."
        echo "\033[1mNo need to ask, he's a smooth operator.\033[0m"
        sleep 3
    else
        echo "Application crashed."
        break
    fi
done
