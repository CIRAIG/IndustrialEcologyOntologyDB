FROM node:22.13.1-alpine

WORKDIR code

# Adds our application code to the image
COPY . .

# Install NPM requirements
RUN npm install

EXPOSE 4200