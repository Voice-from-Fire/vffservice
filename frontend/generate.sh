#!/bin/bash
tmp_dir=`mktemp -d`
json="$tmp_dir/openapi.json"
wget http://localhost:8000/openapi.json -O $json
npx openapi -i $json -o src/generated/api
rm -rf $tmp_dir