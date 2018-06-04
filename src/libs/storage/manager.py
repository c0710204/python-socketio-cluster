import os
import sys
class manager(object):
    instance = None
    file_dict={}
    configs={"load_on_get":False}
    root_path="/dev/shm"
    base_path="/dev/shm"
    num_count = 0
    def __new__(cls, *args, **kw):
        if not cls.instance:
            # cls.instance = object.__new__(cls, *args)
            cls.instance = super(manager, cls).__new__(cls, *args, **kw)
            import random
            
            rand=random.SystemRandom()
            root_path="{1}/{0:10}".format(cls.base_path,rand.randint(1,999999999))
            os.makedirs(root_path, mode=0o777)
        self.__class__.num_count += 1  
        return cls.instance
    def __del__(self):
        import os
        
    def allocate_file(self,obj):

    def registe_path(self,id, path):
        raise NotImplementedError
    def registe_file(self,file):

        raise NotImplementedError
    
    def remove(self,file):
        raise NotImplementedError
    def remove_by_id(self,id):
        raise NotImplementedError

    def get(self,id):
        raise NotImplementedError
    
    def config(dict):
        pass
