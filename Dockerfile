FROM python:3.10-alpine3.18
ENV MONGO_HOST "mongo"
ENV MONGO_PORT 27017
ENV MONGO_USER "bioapi"
ENV MONGO_PASSWORD "bioapi"
ENV MONGO_DB "bio_api"

# The number of gunicorn's worker processes for handling requests.
ENV WEB_CONCURRENCY 1

# Installs Python requirements
RUN pip install --upgrade pip
ADD ./config/bioapi_conf/requirements.txt /config/requirements.txt
RUN pip install -r /config/requirements.txt

# Flask app
ADD ./bio-api /app

# Creates logs directory
RUN mkdir /logs

# Needed to make docker-compose `command` work
WORKDIR /app

# Runs Gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "bioapi:app", "--timeout", "3600"]
