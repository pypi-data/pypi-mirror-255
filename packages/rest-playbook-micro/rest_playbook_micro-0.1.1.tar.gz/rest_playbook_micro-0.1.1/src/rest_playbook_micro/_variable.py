
class Variable():

    name: str
    value: str

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)
        #self.name = f"%ENV_{self.name}%"

    def print(self):
        print(f"{self.name} - {self.value}")
