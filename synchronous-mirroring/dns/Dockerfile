# Specify the base image
FROM node:14-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Bundle app source
COPY . .

# Your app binds to port 80, make sure you expose it.
EXPOSE 3002

# Define the command to run the app
CMD [ "node", "server.js" ]
