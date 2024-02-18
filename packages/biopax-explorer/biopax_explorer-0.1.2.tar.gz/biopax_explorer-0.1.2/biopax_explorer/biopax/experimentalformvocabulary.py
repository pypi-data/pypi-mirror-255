 
from biopax.controlledvocabulary import ControlledVocabulary
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class ExperimentalFormVocabulary(ControlledVocabulary) :


    """
    Class ExperimentalFormVocabulary 
    
              Definition: A reference to the PSI Molecular Interaction ontology (MI)
      participant identification method (e.g. mass spectrometry), experimental role
      (e.g. bait, prey), experimental preparation (e.g. expression level) type.
      Homepage at http://www.psidev.info/.  Browse http://www.ebi.ac.uk/ontology-looku
      p/browse.do?ontName=MI&termId=MI%3A0002&termName=participant%20identification%20
      method  http://www.ebi.ac.uk/ontology-
      lookup/browse.do?ontName=MI&termId=MI%3A0495&termName=experimental%20role
      http://www.ebi.ac.uk/ontology-
      lookup/browse.do?ontName=MI&termId=MI%3A0346&termName=experimental%20preparation

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#ExperimentalFormVocabulary"
  

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
        

