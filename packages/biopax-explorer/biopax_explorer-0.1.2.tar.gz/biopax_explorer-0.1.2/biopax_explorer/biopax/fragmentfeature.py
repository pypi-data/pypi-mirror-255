 
from biopax.entityfeature import EntityFeature
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class FragmentFeature(EntityFeature) :


    """
    Class FragmentFeature 
    
              Definition: An entity feature that represents the resulting physical entity
      subsequent to a cleavage or degradation event.   Usage: Fragment Feature can be
      used to cover multiple types of modfications to the sequence of the physical
      entity:  1.    A protein with a single cleavage site that converts the protein
      into two fragments (e.g. pro-insulin converted to insulin and C-peptide). TODO:
      CV term for sequence fragment?  PSI-MI CV term for cleavage site? 2.    A
      protein with two cleavage sites that removes an internal sequence e.g. an intein
      i.e. ABC -> A 3.    Cleavage of a circular sequence e.g. a plasmid.  In the case
      of removal ( e.g. intron)  the fragment that is *removed* is specified in the
      feature location property. In the case of a "cut" (e.g. restriction enzyme cut
      site) the location of the cut is specified instead. Examples: Insulin Hormone

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#FragmentFeature"
  

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
        

