import uos as os

class TestUtil:
     
    @staticmethod
    def FileExists(path):
        f_exists = True
        try:
            f = open(path)
            f.close()
        except OSError:
            f_exists = False
    
        return f_exists