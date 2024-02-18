 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class PathwayStep(UtilityClass) :


    """
    Class PathwayStep 
    
              Definition: A step in an ordered pathway. Rationale: Some pathways can have a
      temporal order. For example,  if the pathway boundaries are based on a
      perturbation phenotype link, the pathway might start with the perturbing agent
      and end at gene expression leading to the observed changes. Pathway steps can
      represent directed compound graphs. Usage: Multiple interactions may occur in a
      pathway step, each should be listed in the stepProcess property. Order
      relationships between pathway steps may be established with the nextStep slot.
      If the reaction contained in the step is a reversible biochemical reaction but
      physiologically has a direction in the context of this pathway, use the subclass
      BiochemicalPathwayStep.  Example: A metabolic pathway may contain a pathway step
      composed of one biochemical reaction (BR1) and one catalysis (CAT1) instance,
      where CAT1 describes the catalysis of BR1. The M phase of the cell cycle,
      defined as a pathway, precedes the G1 phase, also defined as a pathway.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#PathwayStep"
        self._evidence=kwargs.get('evidence',None)  
        self._nextStep=kwargs.get('nextStep',None)  
        self._stepConversion=kwargs.get('stepConversion',None)  
        self._stepProcess=kwargs.get('stepProcess',None)  
  

##########getter
     
    def get_evidence(self):
        """
        Attribute _evidence  getter
                      Scientific evidence supporting the existence of the entity as described.

                """
        return self._evidence  
     
    def get_nextStep(self):
        """
        Attribute _nextStep  getter
                      The next step(s) of the pathway.  Contains zero or more pathwayStep instances.
      If there is no next step, this property is empty. Multiple pathwayStep instances
      indicate pathway branching.

                """
        return self._nextStep  
     
    def get_stepConversion(self):
        """
        Attribute _stepConversion  getter
                      The central process that take place at this step of the biochemical pathway.

                """
        return self._stepConversion  
     
    def get_stepProcess(self):
        """
        Attribute _stepProcess  getter
                      An interaction or a pathway that are a part of this pathway step.

                """
        return self._stepProcess  
  
##########setter
    
    @validator(value='biopax.Evidence')  
 
    def set_evidence(self,value):
        self._evidence=value  
    
    @validator(value='biopax.PathwayStep')  
 
    def set_nextStep(self,value):
        self._nextStep=value  
    
    @validator(value='biopax.Conversion')  
 
    def set_stepConversion(self,value):
        self._stepConversion=value  
    
    @validator(value='biopax.Interaction')  
 
    def set_stepProcess(self,value):
        self._stepProcess=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['evidence', 'nextStep', 'stepConversion', 'stepProcess']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['evidence']='Evidence'  
      ma['nextStep']='PathwayStep'  
      ma['stepConversion']='Conversion'  
      ma['stepProcess']='Interaction'  
      return ma



    def to_json(self):
        return tojson(self)
        

