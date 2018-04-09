import yaml
import os

class conf(object):
    def __init__(self):
        #read config @target
        self._configs=dict()
    def load(target,path=None):
        if path==None:
            path="config/{0}.yaml".format(target)
        if os.path.isfile(path):
            self._configs[target]=yaml.load(open(path, 'r').read())
        else:
            raise FileNotFoundError
    def __getattr__(self,target):
        if target in self._configs:
            return self._configs[target]
        else:
            raise AttributeError
