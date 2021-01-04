FROM python:3.8.6-slim-buster
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["gunicorn","-w","3","--bind=0.0.0.0:5000","main:appfactory()"]