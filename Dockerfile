FROM postgres:9.6

RUN apt-get update \
	&& apt-get install -y postgresql-server-dev-9.6 ca-certificates build-essential python-dev python-setuptools python-pip pgxnclient \
&& rm -rf /var/lib/apt/lists/*

RUN pgxn install multicorn
RUN pip install requests

ARG API_URL
COPY setup.sh /docker-entrypoint-initdb.d/
COPY src /src
WORKDIR /src
RUN python setup.py install
