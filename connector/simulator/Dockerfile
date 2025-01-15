FROM dcc/bridge

RUN apk update && apk add --no-cache qemu-system-avr \
    && mkdir /io
ADD start.sh /usr/local/bin
ADD CommandStation-EX*.elf /io

ENTRYPOINT ["/usr/local/bin/start.sh"]
