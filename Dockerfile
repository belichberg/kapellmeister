FROM python:3.8-slim as base
ENV PYTHONUNBUFFERED 1

# setup entry point
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -s usr/local/bin/docker-entrypoint.sh / # backwards compat

# working directory
WORKDIR /app

# update pip
RUN pip install --upgrade pip

# Copy requirements.txt
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# install requirement packages from files
RUN pip install --no-cache-dir -r requirements.txt

# COPY
COPY . .

# expose port
EXPOSE 8000

# entry point
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["entry"]
