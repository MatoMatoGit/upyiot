from upyiot.middleware.AvgFilter import AvgFilter
from upyiot.middleware.SubjectObserver.SubjectObserver import Subject
from upyiot.middleware.NvQueue import NvQueue
from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceException
from micropython import const


class SensorException(ServiceException):

    def __init__(self):
        super().__init__()


class SensorService(Service):
    SENSOR_SERVICE_MODE = Service.MODE_RUN_PERIODIC

    def __init__(self, name):
        super().__init__("Sns_" + name, self.SENSOR_SERVICE_MODE, {})


class Sensor(SensorService):
    FILE_SAMPLES_MAX        = const(9999)
    SAMPLE_FMT              = "<i"
      
    def __init__(self, directory, name, filter_depth, sensor_abs):
        # Initialize the SensorService class
        super().__init__(name)

        self.SensorAbstraction = sensor_abs
        self.Filter = AvgFilter.AvgFilter(filter_depth)
        self.SampleQueue = NvQueue.NvQueue(directory + '/' + name, Sensor.SAMPLE_FMT, Sensor.FILE_SAMPLES_MAX)
        self.NewSample = Subject()

    def SvcRun(self):
        self.Read()

    @property  
    def ValueAverage(self):
        return self.NewSample.State
    
    @property
    def SamplesCount(self):
        return self.SampleQueue.Count
    
    def SamplesGet(self, sample_buf):
        self._SamplesLoad(sample_buf)
        return self.SampleQueue.Count
  
    def SamplesClear(self):
        self.SampleQueue.Clear()
        
    def SamplesDelete(self):
        self.SampleQueue.Delete()
    
    def FilterReset(self):
        self.Filter.Reset()
        
    def Read(self):
        self._SampleProcess(self.SensorAbstraction.Read())
        return self.NewSample.State
    
    def ObserverAttachNewSample(self, observer):
        self.NewSample.Attach(observer)

    def _SampleProcess(self, sample):
        self.Filter.Input(sample)
        avg_sample = self.Filter.Output()
        self._SampleStore(avg_sample)
        self.NewSample.State = avg_sample

    def _SampleStore(self, sample):
        self.SampleQueue.Push(sample)

    def _SamplesLoad(self, sample_buf):
        print("Dumping {} samples:".format(self.SampleQueue.Count))
        i = 0
        num_samples = self.SampleQueue.Count
        for i in range(0, num_samples):
            sample_buf[i] = self.SampleQueue.Pop()[0]

