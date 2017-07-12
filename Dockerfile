FROM ubuntu:xenial

USER root

RUN apt update

RUN apt -y install python-dev python-pip gromacs openbabel
RUN pip install pip --upgrade 
RUN pip install matplotlib --upgrade

COPY ./angle_histogram.py angle_histogram
RUN mv angle_histogram /bin/angle_histogram
RUN chmod a+x /bin/angle_histogram

WORKDIR /data/
#RUN cp /bin/angle_histogram /data/angle_histogram
ENTRYPOINT ["angle_histogram"]



  

