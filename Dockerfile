FROM metabrainz/python:3.8-20210115

# remove expired let's encrypt certificate and install new ones
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

##############
# MetaBrainz #
##############

RUN mkdir /code
WORKDIR /code

# Node and dependencies
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs
COPY ./package.json /code/
RUN npm install

# Python dependencies
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
                        build-essential \
                        git \
                        libpq-dev \
                        libtiff5-dev \
                        libffi-dev \
                        libxml2-dev \
                        libxslt1-dev \
                        libssl-dev \
     && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /code/
RUN pip3 install pip==21.0.1
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uWSGI==2.0.15

COPY . /code/
RUN ./node_modules/.bin/lessc ./metabrainz/static/css/main.less > ./metabrainz/static/css/main.css
RUN ./node_modules/.bin/lessc ./metabrainz/static/css/theme/boostrap/boostrap.less > ./metabrainz/static/css/theme/boostrap/boostrap.css
RUN ./node_modules/.bin/lessc ./metabrainz/static/fonts/font_awesome/less/font-awesome.less > ./metabrainz/static/fonts/font_awesome/less/font-awesome.css

############
# Services #
############

# Consul Template service is already set up with the base image.
# Just need to copy the configuration.
COPY ./docker/prod/consul-template-uwsgi.conf /etc/

COPY ./docker/prod/uwsgi.service /etc/service/uwsgi/run
RUN chmod 755 /etc/service/uwsgi/run
COPY ./docker/prod/uwsgi.ini /etc/uwsgi/uwsgi.ini

EXPOSE 13031

ARG GIT_COMMIT_SHA
ENV GIT_SHA ${GIT_COMMIT_SHA}
