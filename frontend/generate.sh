#!/bin/bash

rm -f /tmp/openapi.json
wget http://localhost:8000/openapi.json
npx openapi -i /tmp/openapi.json -o src/generated/api
rm /tmp/openapi.json