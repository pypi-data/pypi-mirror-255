 
from biopax.conversion import Conversion
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Transport(Conversion) :


    """
    Class Transport 
    
              Definition: An conversion in which molecules of one or more physicalEntity pools
      change their subcellular location and become a member of one or more other
      physicalEntity pools. A transport interaction does not include the transporter
      entity, even if one is required in order for the transport to occur. Instead,
      transporters are linked to transport interactions via the catalysis class.
      Usage: If there is a simultaneous chemical modification of the participant(s),
      use transportWithBiochemicalReaction class.  Synonyms: translocation.  Examples:
      The movement of Na+ into the cell through an open voltage-gated channel.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Transport"
  

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
        

