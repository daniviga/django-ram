FROM python:3.10-alpine

RUN mkdir /opt/dcc && pip -q install pyserial
ADD net-to-serial.py config.ini /opt/dcc
RUN python3 -q -m compileall /opt/dcc/net-to-serial.py

EXPOSE 2560/tcp

CMD ["python3", "/opt/dcc/net-to-serial.py"]
