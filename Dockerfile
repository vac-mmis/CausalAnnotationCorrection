FROM python:3.8.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update 
RUN apt-get install -y wget
RUN apt-get install -y unzip

RUN groupadd cac
RUN useradd -m -g cac -s /bin/bash cac

RUN mkdir -p / home/cac

WORKDIR /home/cac

#Installing the acheck package from pip
RUN pip install acheck

# Install the KCL-Planning/VAL suite for validator
RUN wget "https://dev.azure.com/schlumberger/4e6bcb11-cd68-40fe-98a2-e3777bfec0a6/_apis/build/builds/77/artifacts?artifactName=linux64&api-version=7.0&%24format=zip" -O val.zip
RUN unzip val.zip
RUN rm val.zip
RUN unzip linux64/Val-20211204.1-Linux.zip
RUN rm -rf linux64
RUN acheck config -v Val-20211204.1-Linux/bin/Validate

#Install enchant and all spellchecking libraries
RUN apt-get install -y enchant
RUN apt-get install -y aspell-de


WORKDIR /home/cac/CausalAnnotationCorrection

RUN chown -R cac:cac /home/cac
USER cac

CMD bash


