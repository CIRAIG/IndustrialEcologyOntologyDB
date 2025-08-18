FROM python:buster

# Install nodejs from binary to have exact version matching
ARG NODE_VERSION=16.14.2
ARG NODE_PACKAGE=node-v$NODE_VERSION-linux-x64
ARG NODE_HOME=/opt/$NODE_PACKAGE
ENV NODE_PATH $NODE_HOME/lib/node_modules
ENV PATH $NODE_HOME/bin:$PATH
RUN curl https://nodejs.org/dist/v$NODE_VERSION/$NODE_PACKAGE.tar.gz | tar -xzC /opt/

WORKDIR code

# Adds our application code to the image
COPY . .

# Install PIP requirements
RUN pip install -r requirements.txt

# Install NPM requirements
RUN npm install

# Fix ghp-import: error: detected dubious ownership in repository at '/code'
RUN git config --global --add safe.directory /code
