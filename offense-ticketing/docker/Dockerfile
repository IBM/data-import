#
# Dockerfile for a sample ticketing system for a sample to show
# a way to integrate QRadar Offenses into a separate Ticketing System
#
FROM ubuntu:14.04
MAINTAINER Peter Manahan <manahan@ca.ibm.com>

# get the latest packages
RUN apt-get -qq update
RUN apt-get -qqy upgrade

#need git for osticket
#RUN DEBIAN_FRONTEND=noninteractive apt-get -qqy install git


RUN echo 'mysql-server mysql-server/root_password password tick_dbroot' | debconf-set-selections
RUN echo 'mysql-server mysql-server/root_password_again password tick_dbroot' | debconf-set-selections

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install  mysql-server


