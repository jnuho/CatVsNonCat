# FROM node:14

# # Create app node
# WORKDIR /usr/src/app

# # Install app dependencies
# # A wildcard is used to ensure both package.json AND package-lock.json are copied
# # where available (npm@5+)
# # Copying package.json and package-lock.json before running npm install
# # to ensure that the correct version of npm is used to install dependencies
# COPY package*.json ./
# RUN npm install

# # Bundle app source
# COPY *.js ./
# EXPOSE 8080
# CMD [ "node", "server.js" ]

FROM nginx:alpine
# Use an official OpenResty image as the base image
#FROM openresty/openresty:alpine


# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Replace it with our custom Nginx configuration file
# COPY ./web/simple.conf /etc/nginx/conf.d/
COPY ./web/simple.conf /etc/nginx/conf.d/


# Create /var/log/nginx/ directory and symbolic links for access.log and error.log
# redirect logs into stdout and stderr!!
# The integration between the container runtime (e.g., Docker)
# and the kubelet (a Kubernetes component running on each node) is standardized using the Container Runtime Interface (CRI) logging format.
# When a container writes logs to stdout or stderr, the kubelet captures those logs.
# The kubelet makes these logs available to clients (such as developers or administrators) via a special feature of the Kubernetes API.
RUN mkdir -p /var/log/nginx/ && \
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Copy static files to a different directory in the Nginx server
COPY ./web/src /usr/share/nginx/html/src
COPY ./web/index.html /usr/share/nginx/html
COPY ./web/favicon.ico /usr/share/nginx/html
#COPY ./web/src /usr/local/openresty/nginx/html/src
#COPY ./web/index.html /usr/local/openresty/nginx/html


# Expose port 80
EXPOSE 80

# Start Nginx when the container has provisioned
# NOTE : 'nginx -t' to check syntax error before deploying!
CMD ["nginx", "-g", "daemon off;"]
#CMD ["openresty", "-g", "daemon off;"]

