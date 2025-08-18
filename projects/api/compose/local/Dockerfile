FROM python:3.12
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE true

# Install platform's packages required for WeasyPrint
RUN apt-get update
RUN apt-get -y install build-essential python3-dev python3-pip \
python3-setuptools python3-wheel python3-cffi \
libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY /compose/local/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY /compose/local/start /start  
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY /compose/local/celery-worker-start /celery-worker-start
RUN sed -i 's/\r$//g' /celery-worker-start
RUN chmod +x /celery-worker-start

COPY /compose/local/celery-beat-start /celery-beat-start
RUN sed -i 's/\r$//g' /celery-beat-start
RUN chmod +x /celery-beat-start

COPY /compose/local/celery-flower-start /celery-flower-start
RUN sed -i 's/\r$//g' /celery-flower-start
RUN chmod +x /celery-flower-start

ENTRYPOINT ["/entrypoint"]