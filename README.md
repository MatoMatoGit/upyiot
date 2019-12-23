[![Documentation Status](https://readthedocs.org/projects/upyiot/badge/?version=latest)](https://upyiot.readthedocs.io/en/latest/?badge=latest)

# upyiot
Micropython IoT SDK

This repository provides a set of packages and tools to ease development of IoT devices running Micropython.

## Repo structure

* upyiot: Source code folder
    * drivers: Driver libraries
    * middleware: Middleware libraries
    * comm: Communication libraries
    * system: System and cross-cutting libraries

* test: Test folder
    * stubs: Stub libraries used by tests.

* tools: Tools folder

* doc: Documentation folder

## Libraries
All available libraries can be found in the list below.

* drivers
   * Led
      ** Led: Simple LED driver with PWM support.
      ** RgbLed: Simple RGB LED driver with PWM support.
   * Adc
      ** AdcADS101x: TI ADS101x ADC driver. 4 Channel ADC IC with I2C interface. [Datasheet](http://www.ti.com/lit/ds/symlink          /ads1015.pdf)
   * Sensors
      * SensorBase: Sensor base class.
      * BatteryLevel: LIPO battery volage sensor.
      * CapMoisture: Capacitive moisture sensor, based on a frequency counter.
      * Mcp9700Temp: MCP9700 temperature sensor.
      * PhTLight: Phototransistor based light sensor.
   * Sleep
      * DeepSleep: Deep-sleep driver.
   * Switches
      * TactSwitch: Tactile switch driver with press, relese and hold callbacks.

* middleware
   * AvgFilter: Averaging filter.
   * SubjectObserver: Subject and Observer classes. Eases implementation of the Subject-Observer pattern.
   * StructFile: Persistent storage of struct objects.
   * Sensor: Generic sensor service, works with any sensor driver that implements the SensorBase class. Stores samples in a file. Optional sample averaging.
   * NvQueue: Queue data structure in a file.
   * Config: Configuration database and parsers.

* comm   
   * NetCon: WLAN Network connection management service. Supports AP and Station mode.
   * Messaging: Message exchange service between node and server in JSON over MQTT.
   * Web: Simple webserver service.
* system
   * ExtLogging: Extended logging library with file and stream support.
   * Power
      * BatteryMonitor: Battery level monitor.
   * Service
      * Service: Base clase. Used by classes that provide a service.
      * ServiceScheduler: Simple service scheduler with dependency detection and deep-sleep support.
   * SystemTime: Time sychronization service. Periodically synchronizes the internal RTC to NTP. 

