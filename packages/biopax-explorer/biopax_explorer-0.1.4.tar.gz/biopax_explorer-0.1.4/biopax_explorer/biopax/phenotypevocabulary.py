 
from biopax.controlledvocabulary import ControlledVocabulary
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class PhenotypeVocabulary(ControlledVocabulary) :


    """
    Class PhenotypeVocabulary 
    
              Definition: The phenotype measured in the experiment e.g. growth rate or
      viability of a cell. This is only the type, not the value e.g. for a synthetic
      lethal interaction, the phenotype is viability, specified by ID: PATO:0000169,
      "viability", not the value (specified by ID: PATO:0000718, "lethal (sensu
      genetics)". A single term in a phenotype controlled vocabulary can be referenced
      using the xref, or the PhenoXML describing the PATO EQ model phenotype
      description can be stored as a string in PATO-DATA.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#PhenotypeVocabulary"
        self._patoData=kwargs.get('patoData',None)  
  

##########getter
     
    def get_patoData(self):
        """
        Attribute _patoData  getter
                      The phenotype data from PATO, formatted as PhenoXML (defined at
      http://www.fruitfly.org/~cjm/obd/formats.html)

                """
        return self._patoData  
  
##########setter
    
    @validator(value=str)  
 
    def set_patoData(self,value):
        self._patoData=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['patoData']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['patoData']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

