 
from biopax.control import Control
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Modulation(Control) :


    """
    Class Modulation 
    
              Definition: A control interaction in which a physical entity modulates a
      catalysis interaction.   Rationale: Biologically, most modulation interactions
      describe an interaction in which a small molecule alters the ability of an
      enzyme to catalyze a specific reaction. Instances of this class describe a
      pairing between a modulating entity and a catalysis interaction.  Usage:  A
      typical modulation instance has a small molecule as the controller entity and a
      catalysis instance as the controlled entity. A separate modulation instance
      should be created for each different catalysis instance that a physical entity
      may modulate, and for each different physical entity that may modulate a
      catalysis instance. Examples: Allosteric activation and competitive inhibition
      of an enzyme's ability to catalyze a specific reaction.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Modulation"
  

##########getter
  
##########setter
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      return ma



    def to_json(self):
        return tojson(self)
        

