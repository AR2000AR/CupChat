class LimFile():
    def __init__(self,path,lenght):
        self._l = lenght+1
        self._path = path
        self._buffer=[]
        try:
            with open(path,"r") as file:
                for line in file:
                    self._buffer.append(line)
        except FileNotFoundError:
            pass
    def write(self,string):
        if string[-1]!="\n":
            string=string+"\n"
        self._buffer.append(string)
        if len(self._buffer) >= self._l:
            del self._buffer[0]
        with open(self._path,"w") as file:
            for line in self._buffer:
                file.write(line)
