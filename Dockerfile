FROM python:3.8-slim as base
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
RUN mkdir /app/data
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]