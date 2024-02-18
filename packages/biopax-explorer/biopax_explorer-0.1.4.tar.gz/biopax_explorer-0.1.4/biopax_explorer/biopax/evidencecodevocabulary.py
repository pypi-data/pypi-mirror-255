 
from biopax.controlledvocabulary import ControlledVocabulary
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class EvidenceCodeVocabulary(ControlledVocabulary) :


    """
    Class EvidenceCodeVocabulary 
    
              Definition: A reference to the PSI Molecular Interaction ontology (MI)
      experimental method types, including "interaction detection method",
      "participant identification method", "feature detection method". Homepage at
      http://www.psidev.info/.  Browse at http://www.ebi.ac.uk/ontology-
      lookup/browse.do?ontName=MI  Terms from the Pathway Tools Evidence Ontology may
      also be used. Homepage http://brg.ai.sri.com/evidence-ontology/

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#EvidenceCodeVocabulary"
  

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
        

