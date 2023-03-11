FROM dcc/net-to-serial

RUN apk update && apk add qemu-system-avr && mkdir /io
ADD start.sh /usr/local/bin
ADD CommandStation-EX*.elf /io

ENTRYPOINT ["/usr/local/bin/start.sh"]
