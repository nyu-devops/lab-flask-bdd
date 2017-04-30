# Start with a Linux micro-container to keep the image tiny
FROM alpine:3.3

# Document who is responsible for this image
MAINTAINER John Rofrano "rofrano@us.ibm.com"

# Install just the Python runtime (no dev)
# RUN apk add --update \
#     python \
#     py-pip \
#  && rm -rf /var/cache/apk/*
RUN apk --no-cache add \
    python \
    py-pip

# Expose any ports the app is expecting in the environment
ENV PORT 5000
EXPOSE $PORT

# Set up a working folder and install the pre-reqs
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Add the code as the last Docker layer because it changes the most
ADD . /app

# Run the service
CMD [ "python", "run.py" ]
