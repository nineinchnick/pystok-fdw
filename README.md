# pystok-fdw

A demo of FDW in PostgreSQL using Multicorn for the PyStok meetups.

https://docs.google.com/presentation/d/1L3-mxOY_WK174aHYDIigJk33NyqAG0tcxkIz-ZFe0O8/edit?usp=sharing

## HTTP API

```bash
docker build -t api api
docker run --name api -p 8080:80 -d api
```

```bash
http localhost:8080/groups name=default
http localhost:8080/users name=jan groups_collection:='[1]'
http localhost:8080/users?relations=_all
http localhost:8080/groups?relations=_all
```

```
HTTP/1.1 200 OK
Connection: close
Date: Sat, 06 May 2017 09:49:32 GMT
Server: gunicorn/19.7.1
content-length: 201
content-type: application/json; charset=UTF-8
x-api-returned: 3
x-api-total:

{
    "results": [
        {
            "groups_collection": [
                {
                    "id": 1,
                    "name": "default"
                }
            ],
            "id": 3,
            "name": "jan"
        }
    ],
    "returned": 3,
    "total": null
}
```

## FDW

```bash
docker build --build-arg API_URL="http://api:80" -t pystok-fdw .
docker run --name pystok-fdw -e POSTGRES_PASSWORD=pystok --link api:api -d pystok-fdw
docker run -it --rm --link pystok-fdw:postgres postgres psql -h postgres -U postgres
```

```sql
SET client_min_messages = DEBUG;
SELECT * FROM users;
```
