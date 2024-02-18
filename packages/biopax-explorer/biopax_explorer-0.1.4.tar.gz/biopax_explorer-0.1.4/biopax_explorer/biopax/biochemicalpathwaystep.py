 
from biopax.pathwaystep import PathwayStep
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class BiochemicalPathwayStep(PathwayStep) :


    """
    Class BiochemicalPathwayStep 
    
              Definition: Imposes ordering on a step in a biochemical pathway.  Retionale: A
      biochemical reaction can be reversible by itself, but can be physiologically
      directed in the context of a pathway, for instance due to flux of reactants and
      products.  Usage: Only one conversion interaction can be ordered at a time, but
      multiple catalysis or modulation instances can be part of one step.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#BiochemicalPathwayStep"
        self._stepConversion=kwargs.get('stepConversion',None)  
        self._stepDirection=kwargs.get('stepDirection',None)  
  

##########getter
     
    def get_stepConversion(self):
        """
        Attribute _stepConversion  getter
                      The central process that take place at this step of the biochemical pathway.

                """
        return self._stepConversion  
     
    def get_stepDirection(self):
        """
        Attribute _stepDirection  getter
                      Direction of the conversion in this particular pathway context.  This property
      can be used for annotating direction of enzymatic activity. Even if an enzyme
      catalyzes a reaction reversibly, the flow of matter through the pathway will
      force the equilibrium in a given direction for that particular pathway.

                """
        return self._stepDirection  
  
##########setter
    
    @validator(value='biopax.Conversion')  
 
    def set_stepConversion(self,value):
        self._stepConversion=value  
    
    @validator(value=str)  
 
    def set_stepDirection(self,value):
        enum_val=['REVERSIBLE', 'RIGHT-TO-LEFT', 'LEFT-TO-RIGHT']
        if value not in enum_val:
           raise Exception("value of stepDirection not in   ['REVERSIBLE', 'RIGHT-TO-LEFT', 'LEFT-TO-RIGHT']")
        self._stepDirection=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['stepConversion']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['stepDirection']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['stepConversion']='Conversion'  
      ma['stepDirection']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

