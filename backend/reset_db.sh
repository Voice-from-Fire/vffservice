#!/bin/bash
set -e

source envs/env.sh

export PGPASSWORD=$DB_PASSWORD
psql -U $DB_USER -h $DB_HOST -c "DROP DATABASE $DB_NAME" || true
psql -U $DB_USER -h $DB_HOST -c "CREATE DATABASE $DB_NAME"
python3 -m app initdb --create-test-user
