FROM mongo:6.0

WORKDIR /docker-entrypoint-initdb.d/

#copies initialization scripts into the container
#runs the scripts every time the container is started
COPY ./init/ /docker-entrypoint-initdb.d/

#default port
EXPOSE 27017
