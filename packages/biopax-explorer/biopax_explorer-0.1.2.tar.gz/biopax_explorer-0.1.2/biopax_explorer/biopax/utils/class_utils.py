import json

def tostring(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
        
    cls.__str__ = __str__
    return cls



class CustomEncoderShort(json.JSONEncoder):
    """
    A Class to limit recursion in serialization
    """
    def __init__(self, *args, **kwargs):
        self.recursion_limit = kwargs.pop('recursion_limit', 2)  # Set your desired recursion limit
        super().__init__(*args, **kwargs)

    def default(self, obj):
        #print("self.current_level:",self.current_level)
        if hasattr(obj, '__dict__'):
            if self.current_level >= self.recursion_limit:
                 return  self.subobjrep(obj)
            self.current_level += 1
            attributes = vars(obj)  # or obj.__dict__
            attd={}
            for k in attributes.keys():
               
               if k.startswith("_"):
                  nk=k[1:]
                  attd[nk]=attributes[k]
               elif k=="pk":
                  attd['__uri__']=attributes[k]   
            return attd

        return super().default(obj)

    def encode(self, o):
        self.current_level = 1
        return super().encode(o)

    def subobjrep(self,obj):
        return f"{type(obj).__name__}(...)" 

class CustomEncoder(CustomEncoderShort):
     """
    CustomEncoder : a Custom Class for instance serialization
    """ 
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

     def subobjrep(self,obj):
        m={}
        m['__class__']=f"{type(obj).__name__}"  
        m['uri']=obj.pk
        return m   

def tojson(o):
        attributes = vars(o)  
        attd={}
        for k in attributes.keys():
          if k.startswith("_"):
                nk=k[1:]
                attd[nk]=attributes[k]
          elif k=="pk":
                attd['uri']=attributes[k]     
        class_name = type(o).__name__
        attd["__class__"]=class_name
        
        return json.dumps(attd, indent=2, cls=CustomEncoder)    