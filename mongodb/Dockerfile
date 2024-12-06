FROM mongo:6.0

WORKDIR /docker-entrypoint-initdb.d/

COPY ./init/ /docker-entrypoint-initdb.d/

#default port
EXPOSE 27017
