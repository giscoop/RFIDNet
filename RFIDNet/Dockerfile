FROM python:3
COPY .  /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt &&\
    apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]