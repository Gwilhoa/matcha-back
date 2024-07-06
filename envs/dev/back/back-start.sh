#!/bin/bash

source envs/shared/back/back-start-shared.sh

if [ "$TEST_MODE" == "true" ]; then
    pytest -p no:warnings
    exit $?
else
    python app/main.py
fi

