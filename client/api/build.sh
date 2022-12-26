#!/bin/bash

GENERATOR_URL=https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/6.2.1/openapi-generator-cli-6.2.1.jar

GENERATOR=openapi-generator-cli.jar

set -e

if [ ! -f "$GENERATOR" ]; then
	wget wget $GENERATOR_URL -O $GENERATOR     
fi
	

java -jar $GENERATOR generate -i http://localhost:8000/openapi.json -g dart-dio -c open-generator-config.yaml --enable-post-process-file

flutter pub get	
flutter pub run build_runner build

