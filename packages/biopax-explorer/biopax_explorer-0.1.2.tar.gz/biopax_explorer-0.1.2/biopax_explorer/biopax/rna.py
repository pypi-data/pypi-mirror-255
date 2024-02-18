 
from biopax.physicalentity import PhysicalEntity
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Rna(PhysicalEntity) :


    """
    Class Rna 
    
              Definition: A physical entity consisting of a sequence of ribonucleotide
      monophosphates; a ribonucleic acid. Usage: RNA should be used for pools of
      individual RNA molecules. For describing subregions on those molecules use
      RNARegion. Examples: messengerRNA, microRNA, ribosomalRNA. A specific example is
      the let-7 microRNA.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Rna"
        self._entityReference=kwargs.get('entityReference',None)  
  

##########getter
     
    def get_entityReference(self):
        """
        Attribute _entityReference  getter
                      Reference entity for this physical entity.

                """
        return self._entityReference  
  
##########setter
    
    @validator(value='biopax.EntityReference')  
 
    def set_entityReference(self,value):
        self._entityReference=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['entityReference']
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
      ma['entityReference']='EntityReference'  
      return ma



    def to_json(self):
        return tojson(self)
        

