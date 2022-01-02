FROM dcc/net-to-serial

RUN apk update && apk add qemu-system-avr && mkdir /io
ADD start.sh /opt/dcc
ADD CommandStation-EX-uno-*.elf /io

ENTRYPOINT ["/opt/dcc/start.sh"]
