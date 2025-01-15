# Use a container to implement a serial to net bridge

This uses `ncat` from [nmap](https://nmap.org/ncat/) to bridge a serial port to a network port. The serial port is passed to the Podman command (eg. `/dev/ttyACM0`) and the network port is `2560`.

> [!IMPORTANT]
> Other variants of `nc` or `ncat` may not work as expected.

## Build and run the container

```bash
$ podman buil -t dcc/bridge .
$ podman run -d --group-add keep-groups --device=/dev/ttyACM0:/dev/arduino -p 2560:2560 --name dcc-bridge dcc/bridge
```

It can be tested with `telnet`:

```bash
$ telnet localhost 2560
```
