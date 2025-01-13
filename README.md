# Django Railroad Assets Manager (django-ram)

[![Django CI](https://github.com/daniviga/django-rma/actions/workflows/django.yml/badge.svg)](https://github.com/daniviga/django-rma/actions/workflows/django.yml)

![Screenshot 2023-09-18 at 21-57-33 Company RGS - Railroad Assets Manager](https://github.com/daniviga/django-ram/assets/1818657/d20fbe27-1192-4ab1-a19f-8d2ae50cf781)

A `jff` (just for fun) project that aims to create a
model railroad assets manager that allows to:

- Create a database of assets (model trains) and consists with their metadata
- Manage the database via a simple but rationale backoffice
- Expose main data via an HTML interface to show how beautiful is your collection
  to the outside world
- Act as a DCC++ EX REST API gateway to control assets remotely via DCC.
  By anyone, if you'd like (seriously?).

## Preface

**This project is work in progress**. It is intended for fun only and
it has been developed with a commitment of few minutes a day;
it lacks any kind of documentation, code review, architectural review,
security assesment, pentest, ISO certification, etc.

This project probably doesn't match your needs nor expectations. Be aware.

Your model train may also catch fire while using this software.

Check out [my own instance](https://daniele.mynarrowgauge.org).

## Components

Project is based on the following technologies and components:

- [Django](https://www.djangoproject.com/): *the* web framework
- [Django REST](https://www.django-rest-framework.org/): API for the lazy
- [Bootstrap](https://getbootstrap.com/): for the web frontend
- [Arduino](https://arduino.cc): DCC hardware; you must get one, really
- [DCC++ EX Command Station](https://dcc-ex.com/): DCC firmware; an amazing project
- [DCC++ EX WebThrottle](https://github.com/DCC-EX/WebThrottle-EX): the DCC++ EX web throttle, a slightly modified version

It has been developed with:

- [vim](https://www.vim.org/): because it rocks
- [arduino-cli](https://github.com/arduino/arduino-cli/): a mouse? What the heck?
- [vim-arduino](https://github.com/stevearc/vim-arduino): another IDE? No thanks
- [podman](https://podman.io/): because containers are fancy
- [QEMU (avr)](https://qemu-project.gitlab.io/qemu/system/target-avr.html): QEMU can even make toast!


## Requirements

- Python 3.10+
- A USB port when running Arduino hardware (and adaptors if you have a Mac)

## Web portal installation

### Using containers

coming soon

### Manual installation

Setup your virtualenv

```bash
$ python3 -m venv venv
$ source ./venv/bin/activate
```

Install dependencies

```bash
$ pip install -r requirements.txt
# Development stuff
$ pip install -r requirements-dev.txt
```

Bootstrap Django

```bash
$ cd ram
$ python manage.py migrate
$ python manage.py createsuperuser
```

Run Django

```bash
$ python manage.py runserver
```

Browse to `http://localhost:8000`


## DCC++ EX connector

The DCC++ EX connector exposes an Arduino board running DCC++ EX Command Station,
connected via serial port, to the network, allowing commands to be sent via a
TCP socket. A response generated by the DCC++ EX board is sent to all connected clients,
providing synchronization between multiple clients (eg. multiple JMRI instances).

Its use is not needed when running DCC++ EX from a [WiFi](https://dcc-ex.com/get-started/wifi-setup.html) capable board (like when
using an ESP8266 module or a [Mega+WiFi board](https://dcc-ex.com/advanced-setup/supported-microcontrollers/wifi-mega.html)).

### Customize the settings

The daemon comes with default settings in `config.ini`.
Settings may need to be customized based on your setup.


### Using containers

```bash
$ cd daemons
$ podman build -t dcc/net-to-serial .
$ podman run --init --group-add keep-groups -v /dev/ttyACM0:/dev/arduino -p 2560:2560 dcc/net-to-serial
```

### Manual setup

```bash
$ cd daemons
$ pip install -r requirements.txt
$ python ./net-to-serial.py
```

### Test with a simulator

A [QEMU AVR based simulator](daemons/simulator/README.md) running DCC++ EX is bundled togheter with the `net-to-serial.py`
daemon into a container. To run it:

```bash
$ cd daemons/simulator
$ podman build -t dcc/net-to-serial:sim .
$ podman run --init --cpus 0.1 -d -p 2560:2560 dcc/net-to-serial:sim
```

To be continued ...

## Screenshots

### Frontend

![Screenshot 2023-09-18 at 22-00-39 RGS C-19 #40 - Railroad Assets Manager](https://github.com/daniviga/django-ram/assets/1818657/94834b89-5b17-46e7-9494-a1651d72c072)
---
![Screenshot 2023-09-18 at 21-59-30 RGS 1930s short train - Railroad Assets Manager](https://github.com/daniviga/django-ram/assets/1818657/77f9b7c9-27b3-4a65-bad0-26e9cf77e623)



#### Dark mode

![Screenshot 2023-09-18 at 21-58-22 Company RGS - Railroad Assets Manager](https://github.com/daniviga/django-ram/assets/1818657/c95697c9-0897-46f4-941c-6092271e4743)

---



### Backoffice

![image](https://user-images.githubusercontent.com/1818657/175789937-3e4970a2-b37d-44c3-8605-62dabe209c65.png)
---
![image](https://user-images.githubusercontent.com/1818657/175789946-d7ce882c-1ba6-49b2-8e0a-1144e5c6bc35.png)
---
![image](https://user-images.githubusercontent.com/1818657/175789954-0735a4ea-bcaf-4a45-adbc-64105091b051.png)

### Rest API

![image](https://user-images.githubusercontent.com/1818657/180622471-ade06c84-c73b-41d5-a2a7-02a95b2ffc02.png)





