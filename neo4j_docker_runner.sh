#!/bin/bash
# This script spins up a docker instance

INSTANCE_NAME="neo4j-server"
PASSWORD="password"

docker run \
    --name $INSTANCE_NAME \
    -p7473:7473 -p7474:7474 -p7687:7687 \
    --env NEO4J_dbms_connector_https_advertised__address="localhost:7473" \
    --env NEO4J_dbms_connector_http_advertised__address="localhost:7474" \
    --env NEO4J_dbms_connector_bolt_advertised__address="localhost:7687" \
    -v ~/neo4j/data:/data \
    -v ~/neo4j/logs:/logs \
    -v ~/neo4j/import:/var/lib/neo4j/import \
    -v ~/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/$PASSWORD \
    neo4j:latest