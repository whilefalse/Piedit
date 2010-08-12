class Debug(object):

    def __init__(self, doit):
        self.doit = doit

    def writeln(self,msg=''):
        if self.doit:
            print msg
