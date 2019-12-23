[![Documentation Status](https://readthedocs.org/projects/upyiot/badge/?version=latest)](https://upyiot.readthedocs.io/en/latest/?badge=latest)

# upyiot
Micropython IoT SDK

This repository provides a set of libraries and tools to ease development of IoT devices running Micropython.

## Repo structure

* src: Source code folder
    * drivers: Driver libraries
    * middleware: Middleware libraries
    * comm: Communication libraries
    * app: Application libraries

* test: Test folder
    * stubs: Stub libraries used by tests.

* tools: Tools folder

* doc: Documentation folder

## Libraries
All available libraries can be found in the list below.

* drivers
   * Led: Simple LED driver with PWM support.
   * RgbLed: Simple RGB LED driver with PWM support.
   * AdcADS101x: TI ADS101x ADC driver. 4 Channel ADC IC with I2C interface. [Datasheet](http://www.ti.com/lit/ds/symlink/ads1015.pdf)
   * Battery: LiPO battery monitor.
* middleware
   * AvgFilter: Averaging filter.
   * SubjectObserver: Subject and Observer classes. Eases implementation of the Subject-Observer pattern.
   * StructFile: Persistent storage of struct objects.
   * Sensor: Generic sensor library. Stores samples in a file. Optional sample averaging.
   * NvQueue: Queue data structure in a file.
   * Config: Configuration database and parsers.
* comm   
   * NetCon: WLAN Network connection management. Supports AP and Station mode.
   * Messaging: Message exchange between node and server in JSON over MQTT.
   * Web: Simple webserver.
* app-SystemTime: Time management library. Periodically synchronizes the internal RTC to NTP.
    * upy-socket
    * upy-ustruct
    * upy-uasyncio
    * upy-machine-RTC
* app-Power: Power management library. Provides the following classes: power manager, service power manager, power supply.
    * driver-Battery
    * middleware-SubjectObserver-Subject
    * middleware-StructFile
    * upy-machine
    * upy-uerrno
* app-Notifyer: Provides a user notification service.
    * driver-RgbLed
    * middleware-SubjectObserver-Observer
* app-DataExchange: JSON data exchange over MQTT via sinks and sources.
    * middleware-StructFile
    * upy-umqtt.robust
    * upy-ujson
    * upy-utime
    * upy-uerrno
    * upy-const

