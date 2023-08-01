import zipfile   
import os.path   
import os   

class ZFile(object):   
    def __init__(self, filename, mode='r', basedir=''):   
        self.filename = filename   
        self.mode = mode   
        if self.mode in ('w', 'a'):   
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)   
        else:   
            # read only
            self.zfile = zipfile.ZipFile(filename, self.mode)   
        self.basedir = basedir   
        if not self.basedir:   
            # gen base dir
            self.basedir = os.path.dirname(filename)   
          
    def addfile(self, path, arcname=None):   
        # correct win file name
        path = path.replace('//', '/')   
        if not arcname:   
            # what is the target place in zip file?
            if path.startswith(self.basedir):   
                arcname = path[len(self.basedir):]   
            else:   
                arcname = ''   
        self.zfile.write(path, arcname)   
              
    def addfiles(self, paths):   
        for path in paths:   
            if isinstance(path, tuple):   
                self.addfile(*path)   
            else:   
                self.addfile(path)   
              
    def close(self):   
        self.zfile.close()   
          
    def extract_to(self, path):   
        self.zfile.extractall(path=path)

    def extract(self, filename, path):   
        assert not filename.endswith('/') 

        f = os.path.join(path, filename)   
        dir = os.path.dirname(f)   
        if not os.path.exists(dir):   
            os.makedirs(dir) 
        f = open(f, 'wb')
        f.write(self.zfile.read(filename))  

    #    zipfile.
         
              
if __name__ == "__main__":

    base_path = "E:/ProjectBackup/HandPy/DEVISIGN_G/P01_1/"

    zip_files = os.listdir("E:/ProjectBackup/HandPy/DEVISIGN_G/P01_1/")

   
    zip_file = ZFile( os.path.join(base_path, zip_files[0]))
    zip_file.extract_to('tmp_path')
