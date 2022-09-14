FROM python:3.8

# Installs Python requirements
RUN pip install --upgrade pip
ADD ./config/bioapi_conf/requirements.txt /config/requirements.txt
RUN pip install -r /config/requirements.txt

# Flask app
ADD ./bio-api /app

# Needed to make docker-compose `command` work
WORKDIR /app

# Runs Gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "bioapi:app", "--timeout", "3600"]
