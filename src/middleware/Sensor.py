import AvgFilter
import Log
import os
import ustruct
import uasyncio
from SubjectObserver import Subject

class Sensor(object):
    FILE_SAMPLES_MAX        = 9999
    FILE_OFFSET_MAX         = 9999
    FILE_OFFSET_META        = 0
    FILE_OFFSET_SAMPLE_DATA = 0
    META_FMT                = ""
    META_SIZE               = 0
    SAMPLE_FMT              = ""
    SAMPLE_SIZE             = 0
      
    def __init__(self, directory, name, filter_depth, sensor_abs, interval_ms):
        global FILE_OFFSET_SAMPLE_DATA
        global FILE_OFFSET_META
        global FILE_SAMPLES_MAX
        global FILE_OFFSET_MAX
        global META_FMT
        global META_SIZE
        global SAMPLE_FMT
        global SAMPLE_SIZE
        
        FILE_SAMPLES_MAX = 9999
        FILE_OFFSET_MAX = 9999
        META_FMT = "<hh"
        SAMPLE_FMT = "<i"
        
        self.SensorAbstraction = sensor_abs
        self.NumSamples = 0
        self.Filter = AvgFilter.AvgFilter(filter_depth)
        self.SensorFile = directory + '/' + name
        self.NewSample = Subject()
        self.SampleIntervalMs = interval_ms
        
        FILE_OFFSET_META = 0
        META_SIZE = ustruct.calcsize(META_FMT)
        FILE_OFFSET_SAMPLE_DATA = META_SIZE
        SAMPLE_SIZE = ustruct.calcsize(SAMPLE_FMT)
       
        print("Sample data offset: {}".format(FILE_OFFSET_SAMPLE_DATA))
        
        
        print("Sample size: {}".format(SAMPLE_SIZE))
        print("Meta size: {}".format(META_SIZE))
        
        self.__SensorFileCreate()
        
        self.__SensorFileInit()
            
        print("Number of samples: {}".format(self.NumSamples))                
        print("Current write offset: {}".format(self.WriteOffset))

    
    def __Process(self, sample):
        global FILE_OFFSET_SAMPLE_DATA
        global FILE_OFFSET_NUM_SAMPLES
        
        self.Filter.Input(sample)
        avg_sample = self.Filter.Output()
        
        self.__SensorFileWriteSample(avg_sample)
        
        self.NewSample.State = avg_sample
      
    def ValueAverage(self):
        return self.NewSample.State
    
    def SamplesCountGet(self):
        return self.NumSamples
    
    def SamplesGet(self, buf):
        self.__SensorFileDumpSamples(buf)
        num_samples = self.NumSamples
        self.NumSamples = 0
        return num_samples
  
    def SamplesClear(self):
        self.__SensorFileDelete()
        self.__SensorFileCreate()
        self.__SensorFileInit()
    
    def Reset(self):
        self.LastRawSample = 0
        self.NumSamples = 0
        self.Filter.Reset()
        
    def Read(self):
        self.__Process(self.SensorAbstraction.Read())
        self.SubjectSample.State = self.AvgSample
        return self.NewSample.State
    
    def ObserverAttachNewSample(self, observer):
        self.NewSample.Attach(observer)
    
    async def Service(self):
        self.Read()
        await uasyncio.sleep_ms(self.SampleIntervalMs)
    
    def __SensorFileReadMeta(self, file):
        global FILE_OFFSET_META
        global META_SIZE
        global META_FMT
        
        print("Reading meta")
        try:
            file.seek(FILE_OFFSET_META)
            print("File offset: {}".format(file.tell()))
            meta = file.read(META_SIZE)
        except OSError:
            print("Could not access Sensor file.")
            self.NumSamples = 0
            self.WriteOffset = 0
            return -1
        
        try:
            meta_unpacked = ustruct.unpack(META_FMT, meta)
            self.NumSamples = meta_unpacked[0]
            self.WriteOffset = meta_unpacked[1]
            print("Read metadata: {}".format(meta_unpacked))
            return 0
        except ValueError:
            print("Metadata invalid.");
            self.NumSamples = 0
            self.WriteOffset = 0
            return -1;
            
            
    def __SensorFileWriteMeta(self, file):
        global FILE_OFFSET_META
        global META_SIZE
        global META_FMT
        
        print("Writing meta")
        try:
            file.seek(FILE_OFFSET_META)
            print("File offset: {}".format(file.tell()))
            meta = ustruct.pack(META_FMT, self.NumSamples, self.WriteOffset)
            file.write(meta)
        except OSError:
            print("Could not access Sensor file.")
            
    def __SensorFileWriteSample(self, sample):
        global SAMPLE_FMT
        global SAMPLE_SIZE
        
        try:           
            f = open(self.SensorFile, 'a') 
            f.seek(self.WriteOffset)
            print("Writing sample {} at offset {}".format(sample, f.tell()))
            sample_struct = ustruct.pack(SAMPLE_FMT, sample)
            print("Sample struct: {}".format(sample_struct))
            f.write(sample_struct)
            
            self.WriteOffset += SAMPLE_SIZE
            print("New write offset: {}".format(self.WriteOffset))
            self.NumSamples = self.NumSamples + 1
            print("Number of samples: {}".format(self.NumSamples))
            self.__SensorFileWriteMeta(f)
            
            f.close()
        except OSError:
            print("Could not access Sensor file.")
            try:
                f.close()
                print("File closed after exception")
            except:
                pass
            
            
    def __SensorFileDumpSamples(self, sample_buf):
        global SAMPLE_FMT
        global SAMPLE_SIZE
        global FILE_OFFSET_SAMPLE_DATA
        
        print("Dumping {} samples:".format(self.NumSamples))
        try:
            f = open(self.SensorFile, 'r')
            f.seek(FILE_OFFSET_SAMPLE_DATA)
            
            for i in range(0, self.NumSamples):
                try:
                    print("File offset: {}".format(f.tell()))
                    sample = f.read(SAMPLE_SIZE)
                    sample = ustruct.unpack(SAMPLE_FMT, sample)
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
    
    
    def __SensorFileCreate(self):
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
                
    
    def __SensorFileDelete(self):
        try:
            os.remove(self.SensorFile)
        except OSError:
            print("Failed to remove Sensor file.")

    def __SensorFileInit(self):
        try:
            f = open(self.SensorFile, 'a') 
            if self.__SensorFileReadMeta(f) is -1:
                print("Sensor file is uninitialized. Initializing..")
                self.WriteOffset = FILE_OFFSET_SAMPLE_DATA
                self.NumSamples = 0
                self.__SensorFileWriteMeta(f)
            f.close()
        except OSError:
            print("Could not access Sensor file.")
            try:
                f.close()
                print("File closed after exception")
            except:
                pass 
    
    
    
    