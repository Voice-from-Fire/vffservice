#!/bin/bash

export PGPASSWORD=postgres
psql -h db -U postgres -d voicedb
