FROM python:3.9.6-buster as build

RUN echo \
    && apt-get update \
    && apt-get --yes install apt-file \
    && apt-file update
RUN echo \
    && apt-get --yes install build-essential
# RUN pip install --upgrade pip
RUN pip3 install --upgrade pip

RUN mkdir -p /usr/src/app/backend
WORKDIR /usr/src/app/backend
COPY . /usr/src/app/backend
# RUN pip install -r requirements.txt
RUN pip3 --no-cache-dir install -r requirements.txt

CMD python api_conversation_manager.py