# upyiot
Micropython IoT SDK

This repository provides a set of libraries and tools to ease development of IoT devices running Micropython.

## Repo structure

* src: Source code folder
    * comm: Communication libraries
    * drivers: Driver libraries
    * middleware: Middle-ware libraries

* test: Test folder
    * stubs: Stub libraries

* tools: Tools folder

* doc: Documentation folder

## Libraries
All available libraries can be found in the list below. The dependencies of each respective library (if any) are shown in a sublist. Dependencies containing the prefix 'upy-' are part of the Micropython environment.

* comm-NetCon: WLAN Network connection management. Supports AP and Station mode.
    * upy-network
    * upy-os
    * upy-time
* driver-Led: Simple LED driver with PWM support.
    * upy-machine-Pin
* driver-RgbLed: Simple RGB LED driver with PWM support.
    * driver-Led
* driver-AdcADS101x: TI ADS101x ADC driver. 4 Channel ADC IC with I2C interface. [Datasheet](http://www.ti.com/lit/ds/symlink/ads1015.pdf)
    * upy-machine-Pin
    * upy-machine-I2C
    * upy-time
* middleware-AvgFilter: Averaging filter.
* middleware-Sensor: Generic sensor library. Stores samples in a file. Optional sample averaging.
    * middleware-AvgFilter
    * upy-os
    * upy-ustruct
* middleware-SystemTime: Time management library. Periodically synchronizes the internal RTC to NTP.
    * upy-socket
    * upy-ustruct
    * upy-uasyncio
    * upy-machine-RTC
