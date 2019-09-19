from middleware.AvgFilter import AvgFilter
from middleware.SubjectObserver.SubjectObserver import Subject
from middleware.StructFile import StructFile

try:
    import uasyncio
except:
    pass
from micropython import const

class Sensor(object):
    FILE_SAMPLES_MAX        = const(9999)
    FILE_OFFSET_MAX         = const(9999)
    SAMPLE_FMT              = "<i"
    SAMPLE_SIZE             = 0
      
    def __init__(self, directory, name, filter_depth, sensor_abs):
        self.SensorAbstraction = sensor_abs
        self.Filter = AvgFilter.AvgFilter(filter_depth)
        self.SensorFile = StructFile.StructFile(directory + '/' + name, Sensor.SAMPLE_FMT)
        self.NewSample = Subject()
    
    def _Process(self, sample):
        self.Filter.Input(sample)
        avg_sample = self.Filter.Output()
        self._SampleStore(avg_sample)
        self.NewSample.State = avg_sample
    
    @property  
    def ValueAverage(self):
        return self.NewSample.State
    
    @property
    def SamplesCount(self):
        return self.SensorFile.Count
    
    def SamplesGet(self, buf):
        self._SamplesLoad(buf)
        return self.SensorFile.Count
  
    def SamplesClear(self):
        self.SensoFile.Clear()
        
    def SamplesDelete(self):
        self.SensorFile.Delete()
    
    def FilterReset(self):
        self.Filter.Reset()
        
    def Read(self):
        self._Process(self.SensorAbstraction.Read())
        return self.NewSample.State
    
    def ObserverAttachNewSample(self, observer):
        self.NewSample.Attach(observer)
    
    async def Service(self, t_sleep_sec):
        self.Read()
        await uasyncio.sleep(t_sleep_sec)
            
    def _SampleStore(self, sample):
        self.SensorFile.AppendData(sample)

    def _SamplesLoad(self, sample_buf):

        print("Dumping {} samples:".format(self.SensorFile.Count))
        i = 0
        for sample in self.SensorFile:
            sample_buf[i] = sample[0]
            i = i + 1
    