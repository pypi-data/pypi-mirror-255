class Algo:
    def __init__(self, param, boolean):
        if boolean:
            self.param=param
            
    def process(self):
        print(self.param)

v=Algo('hola', False)
v.process()