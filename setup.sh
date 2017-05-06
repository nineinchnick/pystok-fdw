#!/bin/bash
set -e

echo "Using API URL: ${API_URL:=http://api:80}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE EXTENSION multicorn;
CREATE SERVER multicorn_falcon FOREIGN DATA WRAPPER multicorn OPTIONS (wrapper 'pystok-fdw.falcon-api.FalconApiFDW');

CREATE FOREIGN TABLE groups (
  id integer,
  name character varying
) server multicorn_falcon options (
  url '${API_URL}/groups'
);

CREATE FOREIGN TABLE users (
  id integer,
  name character varying,
  groups_collection json
) server multicorn_falcon options (
  url '${API_URL}/users',
  params 'relations=groups_collection'
);
EOSQL
