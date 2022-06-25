# Django Railroad Assets Manager (django-ram)

[![Django CI](https://github.com/daniviga/django-rma/actions/workflows/django.yml/badge.svg)](https://github.com/daniviga/django-rma/actions/workflows/django.yml)

![image](https://user-images.githubusercontent.com/1818657/175789825-9a03f0ff-a95e-42a2-9611-e14d2817e22f.png)


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

This project probably doesn't match you needs nor expectations. Be aware.

Your model train may also catch fire while using this software.

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

- Python 3.8+
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
TCP socket.

Its use is not needed when running DCC++ EX from a [WiFi](https://dcc-ex.com/get-started/wifi-setup.html) capable board (like when
using an ESP8266 module or a [Mega+WiFi board](https://dcc-ex.com/advanced-setup/supported-microcontrollers/wifi-mega.html)).

### Customize the settings

The daemon comes with default settings in `config.ini`.
Settings may need to be customized based on your setup.


### Using containers

```bash
$ cd daemons
$ podman build -t dcc/net-to-serial .
$ podman run -d -p 2560:2560 dcc/net-to-serial
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

![image](https://user-images.githubusercontent.com/1818657/175789897-9ec4a9bb-9c65-48ef-9b57-ae94e094e6a7.png)
---
![image](https://user-images.githubusercontent.com/1818657/175789901-ef50acd7-8c05-4788-92a2-1bb1280d598c.png)
---
![image](https://user-images.githubusercontent.com/1818657/175790004-18926d23-28f9-45bb-b279-6c26575ae3a5.png)
---
![image](https://user-images.githubusercontent.com/1818657/175790008-62eea2cc-1c41-42df-9026-4cf6e8ef712c.png)


### Backoffice

![image](https://user-images.githubusercontent.com/1818657/175789937-3e4970a2-b37d-44c3-8605-62dabe209c65.png)
---
![image](https://user-images.githubusercontent.com/1818657/175789946-d7ce882c-1ba6-49b2-8e0a-1144e5c6bc35.png)
---
![image](https://user-images.githubusercontent.com/1818657/175789954-0735a4ea-bcaf-4a45-adbc-64105091b051.png)

### Rest API

![image](https://user-images.githubusercontent.com/1818657/175790055-4afc5d4e-1d50-4f5b-beeb-822c2496ed46.png)





