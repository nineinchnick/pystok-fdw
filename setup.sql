CREATE EXTENSION multicorn;
CREATE SERVER multicorn_falcon FOREIGN DATA WRAPPER multicorn OPTIONS (wrapper 'pystok-fdw.falcon-api.FalconApiFDW');

CREATE FOREIGN TABLE groups (
  id integer,
  name character varying
) server multicorn_falcon options (
  url 'http://api:80/groups'
);

CREATE FOREIGN TABLE users (
  id integer,
  name character varying,
  groups groups
) server multicorn_falcon options (
  url 'http://api:80/users',
  params 'relations=groups'
);
