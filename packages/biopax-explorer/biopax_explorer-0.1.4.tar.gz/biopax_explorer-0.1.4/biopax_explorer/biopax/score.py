 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Score(UtilityClass) :


    """
    Class Score 
    
              Definition: A score associated with a publication reference describing how the
      score was determined, the name of the method and a comment briefly describing
      the method. Usage:  The xref must contain at least one publication that
      describes the method used to determine the score value. There is currently no
      standard way of describing  values, so any string is valid. Examples: The
      statistical significance of a result, e.g. "p<0.05".

    
    code generator : rdfobj (author F.Moreews 2023).
    
    """

    ##########constructor

    def __init__(self, *args, **kwargs):
        #args -- tuple of anonymous arguments
        #kwargs -- dictionary of named arguments
        
        self.pk=kwargs.get('pk',None)    
        self.pop_state=kwargs.get('pop_state',None)  
        self.exhausted=kwargs.get('exhausted',None)
        self.meta_label=None  
        
        super().__init__(*args, **kwargs) 
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Score"
        self._scoreSource=kwargs.get('scoreSource',None)  
        self._value=kwargs.get('value',None)  
  

##########getter
     
    def get_scoreSource(self):
        """
        Attribute _scoreSource  getter
                      This property defines the source of the scoring methodology -- a publication or
      web site describing the scoring methodology and the range of values.

                """
        return self._scoreSource  
     
    def get_value(self):
        """
        Attribute _value  getter
                      The value of the score. This can be a numerical or categorical value.

                """
        return self._value  
  
##########setter
    
    @validator(value='biopax.Provenance')  
 
    def set_scoreSource(self,value):
        self._scoreSource=value  
    
    @validator(value=str)  
 
    def set_value(self,value):
        self._value=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['scoreSource']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['value']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['scoreSource']='Provenance'  
      ma['value']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

