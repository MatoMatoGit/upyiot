import AvgFilter
import Log
import os
import ustruct
import uasyncio
from SubjectObserver import Subject
from micropython import const

class Sensor(object):
    FILE_SAMPLES_MAX        = const(9999)
    FILE_OFFSET_MAX         = const(9999)
    FILE_OFFSET_META        = const(0)
    FILE_OFFSET_SAMPLE_DATA = 0
    META_FMT                = "<HH"
    META_SIZE               = 0
    SAMPLE_FMT              = "<i"
    SAMPLE_SIZE             = 0
      
    def _init_(self, directory, name, filter_depth, sensor_abs):
                
        self.SensorAbstraction = sensor_abs
        self.NumSamples = 0
        self.Filter = AvgFilter.AvgFilter(filter_depth)
        self.SensorFile = directory + '/' + name
        self.NewSample = Subject()
        
        Sensor.META_SIZE = ustruct.calcsize(Sensor.META_FMT)
        Sensor.FILE_OFFSET_SAMPLE_DATA = Sensor.META_SIZE
        Sensor.SAMPLE_SIZE = ustruct.calcsize(Sensor.SAMPLE_FMT)
       
        print("Sample data offset: {}".format(Sensor.FILE_OFFSET_SAMPLE_DATA))
        
        
        print("Sample size: {}".format(Sensor.SAMPLE_SIZE))
        print("Meta size: {}".format(Sensor.META_SIZE))
        
        self._SensorFileCreate()
        
        self._SensorFileInit()
            
        print("Number of samples: {}".format(self.NumSamples))                
        print("Current write offset: {}".format(self.WriteOffset))

    
    def _Process(self, sample):
        global FILE_OFFSET_SAMPLE_DATA
        global FILE_OFFSET_NUM_SAMPLES
        
        self.Filter.Input(sample)
        avg_sample = self.Filter.Output()
        
        self._SensorFileWriteSample(avg_sample)
        
        self.NewSample.State = avg_sample
      
    def ValueAverage(self):
        return self.NewSample.State
    
    def SamplesCountGet(self):
        return self.NumSamples
    
    def SamplesGet(self, buf):
        self._SensorFileDumpSamples(buf)
        num_samples = self.NumSamples
        self.NumSamples = 0
        return num_samples
  
    def SamplesClear(self):
        self._SensorFileDelete()
        self._SensorFileCreate()
        self._SensorFileInit()
    
    def Reset(self):
        self.LastRawSample = 0
        self.NumSamples = 0
        self.Filter.Reset()
        
    def Read(self):
        self._Process(self.SensorAbstraction.Read())
        self.SubjectSample.State = self.AvgSample
        return self.NewSample.State
    
    def ObserverAttachNewSample(self, observer):
        self.NewSample.Attach(observer)
    
    async def Service(self, t_sleep_sec):
        self.Read()
        await uasyncio.sleep(t_sleep_sec)
    
    def _SensorFileReadMeta(self, file):

        print("Reading meta")
        try:
            file.seek(Sensor.FILE_OFFSET_META)
            print("File offset: {}".format(file.tell()))
            meta = file.read(Sensor.META_SIZE)
        except OSError:
            print("Could not access Sensor file.")
            self.NumSamples = 0
            self.WriteOffset = 0
            return -1
        
        try:
            meta_unpacked = ustruct.unpack(Sensor.META_FMT, meta)
            self.NumSamples = meta_unpacked[0]
            self.WriteOffset = meta_unpacked[1]
            print("Read metadata: {}".format(meta_unpacked))
            return 0
        except ValueError:
            print("Metadata invalid.");
            self.NumSamples = 0
            self.WriteOffset = 0
            return -1;
            
            
    def _SensorFileWriteMeta(self, file):
        
        print("Writing meta")
        try:
            file.seek(Sensor.FILE_OFFSET_META)
            print("File offset: {}".format(file.tell()))
            meta = ustruct.pack(Sensor.META_FMT, self.NumSamples, self.WriteOffset)
            file.write(meta)
        except OSError:
            print("Could not access Sensor file.")
            
    def _SensorFileWriteSample(self, sample):
        
        try:           
            f = open(self.SensorFile, 'a') 
            f.seek(self.WriteOffset)
            print("Writing sample {} at offset {}".format(sample, f.tell()))
            sample_struct = ustruct.pack(Sensor.SAMPLE_FMT, sample)
            print("Sample struct: {}".format(sample_struct))
            f.write(sample_struct)
            
            self.WriteOffset += Sensor.SAMPLE_SIZE
            print("New write offset: {}".format(self.WriteOffset))
            self.NumSamples = self.NumSamples + 1
            print("Number of samples: {}".format(self.NumSamples))
            self._SensorFileWriteMeta(f)
            
            f.close()
        except OSError:
            print("Could not access Sensor file.")
            try:
                f.close()
                print("File closed after exception")
            except:
                pass
            
            
    def _SensorFileDumpSamples(self, sample_buf):

        print("Dumping {} samples:".format(self.NumSamples))
        try:
            f = open(self.SensorFile, 'r')
            f.seek(Sensor.FILE_OFFSET_SAMPLE_DATA)
            
            for i in range(0, self.NumSamples):
                try:
                    print("File offset: {}".format(f.tell()))
                    sample = f.read(Sensor.SAMPLE_SIZE)
                    sample = ustruct.unpack(Sensor.SAMPLE_FMT, sample)
                    sample = sample[0]
                    sample_buf.append(sample)
                    print("{}:{}".format(i, sample))
                except ValueError:
                    print("{}:Err".format(i))
                    pass               
                
            f.close()
        except OSError:
            print("Could not access Sensor file.")
            try:
                f.close()
                print("File closed after exception")
            except:
                pass        
    
    
    def _SensorFileCreate(self):
        try:
            f = open(self.SensorFile, 'r')
            f.close()
            print("Sensor file already exists")
        except OSError:
            try:
                f = open(self.SensorFile, 'w')
                f.close()
                print("Sensor file created")
            except OSError:
                print("Failed to create Sensor file")
                
    
    def _SensorFileDelete(self):
        try:
            os.remove(self.SensorFile)
        except OSError:
            print("Failed to remove Sensor file.")

    def _SensorFileInit(self):
        try:
            f = open(self.SensorFile, 'a') 
            if self._SensorFileReadMeta(f) is -1:
                print("Sensor file is uninitialized. Initializing..")
                self.WriteOffset = Sensor.FILE_OFFSET_SAMPLE_DATA
                self.NumSamples = 0
                self._SensorFileWriteMeta(f)
            f.close()
        except OSError:
            print("Could not access Sensor file.")
            try:
                f.close()
                print("File closed after exception")
            except:
                pass 
    
    
    
    