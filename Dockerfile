FROM python:3.12-alpine

# install config
RUN mkdir config
RUN apk update && apk add gcc libc-dev make git jpeg-dev zlib-dev
COPY config/aws-root-ca1.cer /config

# install app files
RUN mkdir irbt
COPY irbt /irbt
COPY requirements.txt /
COPY bin/irbt-cli.py /bin/irbt-cli.py

# install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# run app
CMD [ "python", "/bin/irbt-cli.py" ]
