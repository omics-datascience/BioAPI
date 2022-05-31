FROM python:3.8

# Flask app
ADD ./bio-api /app

# Installs Python requirements
RUN pip install --upgrade pip && mkdir /config
ADD ./config/requirements.txt /config/requirements.txt
RUN pip install -r /config/requirements.txt

# Needed to make docker-compose `command` work
WORKDIR /app