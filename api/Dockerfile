FROM python:3.5

RUN apt-get update &&\
    apt-get -y install python3-dev \
                       sqlite3 \
                       python-virtualenv &&\
    apt-get clean &&\

    mkdir -p /app/venv /app/src &&\
    virtualenv -p $(which python3) --no-site-packages /app/venv &&\
    /app/venv/bin/pip install -U setuptools pip

COPY requirements.txt /app/requirements.txt
ENV PATH /app/venv/bin:${PATH}
RUN /app/venv/bin/pip install -r /app/requirements.txt gunicorn

COPY . /app/src/
WORKDIR /app/src/
CMD sqlite3 mydatabase.db < init.sql
CMD /app/venv/bin/gunicorn -b 0.0.0.0:80 --reload app
