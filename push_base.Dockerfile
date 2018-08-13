FROM ubuntu:18.04

RUN echo "Starting build"

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV GEOS_LIBRARY_PATH /usr/lib/x86_64-linux-gnu/libgeos_c.so.1
ENV GDAL_LIBRARY_PATH /usr/lib/libgdal.so

RUN apt-get update && \
    # Development dependencies(necessary )
    apt-get install -y software-properties-common \
    build-essential libpq-dev python-dev \
    python-minimal python-pip libgeos-dev libgdal-dev libssl-dev \
    # Production dependencies
    gdal-bin python git python-gdal libgeos-c1v5 curl && \
    # Python packages
    pip install -U gunicorn && \
    # If we have any kind of problem with gdal, we can try to fix using this repo
    # add-apt-repository ppa:ubuntugis/ubuntugis-unstable
    # Node
    curl -sL https://deb.nodesource.com/setup_8.x | bash - && apt-get install -y nodejs

RUN npm install -g coffeescript less
