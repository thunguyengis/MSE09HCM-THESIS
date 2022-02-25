FROM node:12 as build

RUN mkdir -p /usr/src/app/frontend

WORKDIR /usr/src/app/frontend

COPY . /usr/src/app/frontend

RUN CI=true

RUN npm install

CMD npm start
