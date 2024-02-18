class AuthAnswer():

    def __init__(self, result, error=None, token=None):
        self.result = result
        self.error = error
        self.token = token
    
    def get(self, attr):
        return self.__getattribute__(attr)
