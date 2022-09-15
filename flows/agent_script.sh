#!/bin/bash

# Environment variables must be present:
# PREFECT_API_KEY
# PREFECT_API_URL

echo 'Starting prefect agent'
echo "This is that -> $2"
prefect work-queue create $1
prefect agent start -q $1
