
class DummySensor(object):
    
    def __init__(self, samples):
        self.Samples = samples
        self.NumSamples = len(samples)
        self.Index = 0
        
    
    def Read(self):
        sample = self.Samples[self.Index]
        self.Index = self.Index + 1
        if self.Index >= self.NumSamples:
            self.Index = 0
        return sample