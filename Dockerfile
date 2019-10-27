FROM python:3.7.4-alpine3.9

# install config
RUN mkdir config
RUN apk update && apk add gcc libc-dev make git
COPY config/aws-root-ca1.cer /config

# install app files
RUN mkdir irbt
COPY irbt /irbt
COPY requirements.txt /
COPY cli.py /

# install dependencies
RUN pip install -r requirements.txt

# run app
CMD [ "python", "./cli.py" ]
