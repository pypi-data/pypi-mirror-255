 
from biopax.entityfeature import EntityFeature
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class ModificationFeature(EntityFeature) :


    """
    Class ModificationFeature 
    
              Definition: An entity feature that represents  the covalently modified state of
      a dna, rna or a protein.   Rationale: In Biology, identity of DNA, RNA and
      Protein entities are defined around a wildtype sequence. Covalent modifications
      to this basal sequence are represented using modificaton features. Since small
      molecules are identified based on their chemical structure, not sequence, a
      covalent modification to a small molecule would result in a different molecule.
      Usage: The added groups should be simple and stateless, such as phosphate or
      methyl groups and are captured by the modificationType controlled vocabulary. In
      other cases, such as covalently linked proteins, use CovalentBindingFeature
      instead.   Instances: A phosphorylation on a protein, a methylation on a DNA.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#ModificationFeature"
        self._modificationType=kwargs.get('modificationType',None)  
  

##########getter
     
    def get_modificationType(self):
        """
        Attribute _modificationType  getter
                      Description and classification of the feature.

                """
        return self._modificationType  
  
##########setter
    
    @validator(value='biopax.SequenceModificationVocabulary')  
 
    def set_modificationType(self,value):
        self._modificationType=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['modificationType']
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
      ma['modificationType']='SequenceModificationVocabulary'  
      return ma



    def to_json(self):
        return tojson(self)
        

