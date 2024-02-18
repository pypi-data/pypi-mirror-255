class MasterClass:
    def __init__(self, imgwin):
        self.imgwin = imgwin
        self.exist=0
        self.win=None

    def create(self,mapdata,ps):
        self.mapdata = mapdata
        self.ps = ps
        self.exist=1
        self._create()
        
    def kill(self):
        self.exist=0
        self.win.destroy()
