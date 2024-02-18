

class FileTracker:
    def __init__(self,fn=None):

        self.fn=fn
        self.lastpath=None
        self.wfn=0
        if fn!=None: self.open()

    def open(self):
        if self.fn==None:
            print('Need filename')
            return
        #get file
        try:
            fid=open(self.fn,'rU')
        except:
            print('file does not exist')
            self.lastpath=''
            return
        self.lastpath=fid.readline()
        fid.close()
        
    def save(self):
        if self.fn==None:
            print('Need filename')
            return
        fid=open(self.fn,'w')
        fid.write(self.lastpath)
        fid.close()

    def set(self,path):
        self.lastpath=path

    def get(self):
        return self.lastpath