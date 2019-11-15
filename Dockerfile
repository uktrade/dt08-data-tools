FROM continuumio/miniconda3

# setup environment variables
ENV AWS_DEFAULT_REGION eu-west-2

# setup application files
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app/

# make directory writeable by root group to allow hot copy of files during development
RUN chmod 777 /usr/src/app

# create application environment
RUN conda env create -q -f environment.yml
python

# create long running process to prevent pod crash
RUN touch dummy
CMD tail -f dummy

