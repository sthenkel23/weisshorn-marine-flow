#!/bin/bash

# Environment variables must be present:
# PREFECT_API_KEY
# PREFECT_API_URL

echo 'Starting prefect agent now ... '
prefect agent start -q $1
