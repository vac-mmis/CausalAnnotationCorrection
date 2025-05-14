FROM python:3.9.13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update 
RUN apt-get install -y wget
RUN apt-get install -y unzip
RUN apt-get install -y make

RUN groupadd cac
RUN useradd -m -g cac -s /bin/bash cac

RUN mkdir -p /home/cac/CausalAnnotationCorrection

WORKDIR /home/cac

#Installing the acheck package from pip
RUN pip install acheck

# Install the KCL-Planning/VAL suite for validator
RUN wget "https://dev.azure.com/schlumberger/4e6bcb11-cd68-40fe-98a2-e3777bfec0a6/_apis/build/builds/77/artifacts?artifactName=linux64&api-version=7.0&%24format=zip" -O val.zip
RUN unzip val.zip
RUN rm val.zip
RUN unzip linux64/Val-20211204.1-Linux.zip
RUN rm -rf linux64

# Import config and then set validator path
RUN acheck config -v Val-20211204.1-Linux/bin/Validate

#Install enchant and all spellchecking libraries
RUN apt-get install -y libenchant-2-2 libenchant-2-dev
RUN apt-get install -y aspell-de
RUN apt-get install -y aspell-en
RUN apt-get install -y aspell-fr



WORKDIR /home/cac/CausalAnnotationCorrection
COPY Examples /home/cac/CausalAnnotationCorrection/Examples

RUN chown -R cac:cac /home/cac
USER cac

CMD bash


