FROM python:3.10-alpine

RUN mkdir /opt/dcc && pip -q install pyserial
ADD net-to-serial.py config.ini /opt/dcc

EXPOSE 2560/tcp

CMD ["python3", "/opt/dcc/net-to-serial.py"]
