# import docker file
FROM ghcr.io/project-osrm/osrm-backend

# define variables
ARG DOWNLOAD_URL=http://download.geofabrik.de/north-america/us-northeast-latest.osm.pbf
ARG OSM_FILE=us-northeast-latest.osm.pbf
ARG OSRM_FILE=us-northeast-latest.osrm

# transform variables
ENV OSM_FILE=$OSM_FILE
ENV OSRM_FILE=$OSRM_FILE
ENV DOWNLOAD_URL=$DOWNLOAD_URL

# install wget
RUN apt-get update
RUN apt install -y wget

# download data
RUN mkdir data
RUN cd data
RUN wget $DOWNLOAD_URL

# extract the osm file
RUN osrm-extract -p /opt/car.lua $OSM_FILE
# delete the osm file
RUN rm -rf $OSM_FILE
# create other formats
RUN osrm-partition $OSRM_FILE
RUN osrm-customize $OSRM_FILE

# Start the docker
CMD osrm-routed --algorithm mld $OSRM_FILE

EXPOSE 5000