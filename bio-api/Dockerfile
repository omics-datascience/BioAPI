FROM python:3.6
ADD . /app
WORKDIR /app
RUN /usr/local/bin/python -m pip  install --upgrade pip
RUN pip3  install 'pymongo==3.6.1' --force-reinstall
RUN pip3  install 'Flask==2.0.2' --force-reinstall
RUN pip3  install 'flask-cors==3.0.10' --force-reinstall
RUN pip3  install 'gunicorn==20.1.0' --force-reinstall
RUN pip3  install 'requests==2.26.0' --force-reinstall
RUN pip3  install 'ConfigParser==5.2.0' --force-reinstall
RUN pip3  install pytest coverage
