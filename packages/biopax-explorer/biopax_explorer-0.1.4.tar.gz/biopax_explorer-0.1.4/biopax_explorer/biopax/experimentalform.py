 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class ExperimentalForm(UtilityClass) :


    """
    Class ExperimentalForm 
    
              Definition: The form of a physical entity in a particular experiment, as it may
      be modified for purposes of experimental design. Examples: A His-tagged protein
      in a binding assay. A protein can be tagged by multiple tags, so can have more
      than 1 experimental form type terms

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#ExperimentalForm"
        self._experimentalFeature=kwargs.get('experimentalFeature',None)  
        self._experimentalFormDescription=kwargs.get('experimentalFormDescription',None)  
        self._experimentalFormEntity=kwargs.get('experimentalFormEntity',None)  
  

##########getter
     
    def get_experimentalFeature(self):
        """
        Attribute _experimentalFeature  getter
                      A feature of the experimental form of the participant of the interaction, such
      as a protein tag. It is not expected to occur in vivo or be necessary for the
      interaction.

                """
        return self._experimentalFeature  
     
    def get_experimentalFormDescription(self):
        """
        Attribute _experimentalFormDescription  getter
                      Descriptor of this experimental form from a controlled vocabulary.

                """
        return self._experimentalFormDescription  
     
    def get_experimentalFormEntity(self):
        """
        Attribute _experimentalFormEntity  getter
                      The gene or physical entity that this experimental form describes.

                """
        return self._experimentalFormEntity  
  
##########setter
    
    @validator(value='biopax.EntityFeature')  
 
    def set_experimentalFeature(self,value):
        self._experimentalFeature=value  
    
    @validator(value='biopax.ExperimentalFormVocabulary')  
 
    def set_experimentalFormDescription(self,value):
        self._experimentalFormDescription=value  
    
    @validator(value='biopax.Gene')  
 
    def set_experimentalFormEntity(self,value):
        self._experimentalFormEntity=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['experimentalFeature', 'experimentalFormDescription', 'experimentalFormEntity']
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
      ma['experimentalFeature']='EntityFeature'  
      ma['experimentalFormDescription']='ExperimentalFormVocabulary'  
      ma['experimentalFormEntity']='Gene'  
      return ma



    def to_json(self):
        return tojson(self)
        

