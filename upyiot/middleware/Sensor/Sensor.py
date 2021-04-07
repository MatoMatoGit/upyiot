from upyiot.middleware.AvgFilter import AvgFilter
from upyiot.middleware.SubjectObserver.SubjectObserver import Subject
from upyiot.middleware.NvQueue import NvQueue
from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceException
from upyiot.system.ExtLogging import ExtLogging
from micropython import const


class SensorExceptionInvalidConfig(ServiceException):

    def __init__(self, msg):
        print(msg)
        super().__init__()


class SensorService(Service):
    SENSOR_SERVICE_MODE = Service.MODE_RUN_PERIODIC

    def __init__(self, name):
        super().__init__("Sns_" + name, self.SENSOR_SERVICE_MODE, {})


class Sensor(SensorService):
    FILE_SAMPLES_MAX        = const(9999)
    SAMPLE_FMT              = "<i"
      
    def __init__(self, directory: str, name: str, filter_depth: int, sensor_driver_obj,
                 samples_per_update: int = 1, dec_round: bool = True, store_data: bool = True):
        """

        :param directory:
        :type directory:
        :param name:
        :type name:
        :param filter_depth:
        :type filter_depth:
        :param sensor_driver_obj:
        :type sensor_driver_obj:
        :param samples_per_update:
        :type samples_per_update:
        :param dec_round:
        :type dec_round:
        :param store_data:
        :type store_data:
        """
        if samples_per_update > 1 and store_data is False:
            raise SensorExceptionInvalidConfig("store_data must be True if samples_per_update > 1")

        # Initialize the SensorService class
        super().__init__(name)

        self.SensorDriver = sensor_driver_obj
        self.SamplesPerUpdate = samples_per_update
        self.Filter = AvgFilter.AvgFilter(filter_depth, dec_round)
        if store_data is True:
            self.SampleQueue = NvQueue.NvQueue(directory + '/' + name, Sensor.SAMPLE_FMT, Sensor.FILE_SAMPLES_MAX)
        self.NewSample = Subject()
        self.NewSample.State = list()
        self.StoreData = store_data
        self.Log = ExtLogging.Create("Sensor-{}".format(name))

    def SvcRun(self):
        self.Read()

    @property
    def ValueAverage(self):
        return self.NewSample.State
    
    @property
    def SamplesCount(self) -> int:
        return self.SampleQueue.Count

    def SamplesGet(self) -> tuple:
        """
        Get all the stored samples.
        :return: # of samples, samples
        :rtype: (integer, list)
        """
        return self.SampleQueue.Count, self._SamplesLoad()
  
    def SamplesClear(self):
        self.SampleQueue.Clear()
        
    def SamplesDelete(self):
        self.SampleQueue.Delete()
    
    def FilterReset(self):
        self.Filter.Reset()
        
    def Read(self):
        self.SensorDriver.Enable()
        for i in range(0, self.Filter.Depth):
            val = self.SensorDriver.Read()
            self.Log.debug("Read value: {}".format(val))
            self.Filter.Input(val)
        self.SensorDriver.Disable()
        out = self.Filter.Output()
        self.Log.info("Sensor value: {}".format(out))
        self._SampleProcess(out)
        return out
    
    def ObserverAttachNewSample(self, observer):
        self.NewSample.Attach(observer)

    def _SampleProcess(self, sample):
        if self.StoreData is True:
            self._SampleStore(sample)

        if self.SamplesPerUpdate > 1:
            if self.SamplesCount >= self.SamplesPerUpdate:
                cnt, samples = self.SamplesGet()
                self.Log.debug("Observer update samples ({}): {}".format(cnt, samples))
                self.NewSample.State = samples
        else:
            self.Log.debug("Observer update sample: {}".format(sample))
            self.NewSample.State = sample

    def _SampleStore(self, sample):
        self.Log.debug("Storing sample")
        self.SampleQueue.Push(sample)
        self.Log.info("Total stored samples {}".format(self.SamplesCount))

    def _SamplesLoad(self):
        self.Log.info("Dumping {} samples:".format(self.SampleQueue.Count))
        num_samples = self.SampleQueue.Count
        samples = list()
        for i in range(0, num_samples):
            samples.append(self.SampleQueue.Pop()[0])
        return samples

