


class MyThing(dict):

    def __init__(self, param="paramval"):
        super(dict, self).__init__()
        self._param = param

    @property
    def param(self):
        return self._param
    
	

