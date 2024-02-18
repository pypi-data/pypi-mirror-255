 
from biopax.interaction import Interaction
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class MolecularInteraction(Interaction) :


    """
    Class MolecularInteraction 
    
              Definition: An interaction in which participants bind physically to each other,
      directly or indirectly through intermediary molecules.  Rationale: There is a
      large body of interaction data, mostly produced by high throughput systems, that
      does not satisfy the level of detail required to model them with ComplexAssembly
      class. Specifically, what is lacking is the stoichiometric information and
      completeness (closed-world) of participants required to model them as chemical
      processes. Nevertheless interaction data is extremely useful and can be captured
      in BioPAX using this class.    Usage: This class should be used by default for
      representing molecular interactions such as those defined by PSI-MI level 2.5.
      The participants in a molecular interaction should be listed in the PARTICIPANT
      slot. Note that this is one of the few cases in which the PARTICPANT slot should
      be directly populated with instances (see comments on the PARTICPANTS property
      in the interaction class description). If all participants are known with exact
      stoichiometry, ComplexAssembly class should be used instead.  Example: Two
      proteins observed to interact in a yeast-two-hybrid experiment where there is
      not enough experimental evidence to suggest that the proteins are forming a
      complex by themselves without any indirect involvement of other proteins. This
      is the case for most large-scale yeast two-hybrid screens.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#MolecularInteraction"
  

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
        

