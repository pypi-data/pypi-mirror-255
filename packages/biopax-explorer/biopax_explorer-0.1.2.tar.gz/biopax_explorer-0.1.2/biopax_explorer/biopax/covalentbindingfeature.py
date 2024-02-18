##generated class CovalentBindingFeature
#############################




##   Definition : An entity feature that represent the covalently bound state of  a
##   physical entity.   Rationale: Most frequent covalent modifications to proteins
##   and DNA, such as phosphorylation and metylation are covered by the
##   ModificationFeature class. In these cases, the added groups are simple and
##   stateless therefore they can be captured by a controlled vocabulary. In other
##   cases, such as ThiS-Thilacyl-disulfide, the covalently linked molecules are best
##   represented as a molecular complex. CovalentBindingFeature should be used to
##   model such covalently linked complexes.  Usage: Using this construct, it is
##   possible to represent small molecules as a covalent complex of two other small
##   molecules. The demarcation of small molecules is a general problem and is
##   delegated to small molecule databases.The best practice is not to model using
##   covalent complexes unless at least one of the participants is a protein, DNA or
##   RNA.  Examples: disulfide bond UhpC + glc-6P -> Uhpc-glc-6p acetyl-ACP ->
##   decenoyl-ACP charged tRNA

##############################
 
##############################
 

from biopax.utils.class_utils import tostring
from biopax.utils.validate_utils import CValidateArgType,raise_error


validator = CValidateArgType(raise_error, logger=None)

@tostring
class CovalentBindingFeature :
##multiple inheritance management (['ModificationFeature', 'BindingFeature'])
#no extends here, because python does not manage multiple inheritance. 
# To avoid this limitation, we select the following 
#  design pattern :
# parent attributes are directly copied
##
##########constructor
    def __init__(self, *args, **kwargs):
        #args -- tuple of anonymous arguments
        #kwargs -- dictionary of named arguments
        
        self.pk=kwargs.get('pk',None)    
        self.pop_state=kwargs.get('pop_state',None)  
        self.exhausted=kwargs.get('exhausted',None)  
 
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#CovalentBindingFeature"

##   Description and classification of the feature.

        self._modificationType=kwargs.get('modificationType',None)  
##   A binding feature represents a "half" of the bond between two entities. This
##   property points to another binding feature which represents the other half. The
##   bond can be covalent or non-covalent.

        self._bindsTo=kwargs.get('bindsTo',None)  
##   This flag represents whether the binding feature is within the same molecule or
##   not. A true value implies that the entityReferences of this feature and its
##   binding partner are the same.

        self._intraMolecular=kwargs.get('intraMolecular',None)  
  


##########getter
     
    def get_modificationType(self):
        return self._modificationType  
     
    def get_bindsTo(self):
        return self._bindsTo  
     
    def get_intraMolecular(self):
        return self._intraMolecular  
  
##########setter
    
    @validator(value='biopax.SequenceModificationVocabulary')  
 
    def set_modificationType(self,value):
        self._modificationType=value  
    
    @validator(value='biopax.BindingFeature')  
 
    def set_bindsTo(self,value):
        self._bindsTo=value  
    
    @validator(value=bool)  
 
    def set_intraMolecular(self,value):
        self._intraMolecular=value  
  




    def object_attributes(self):

 
      object_attribute_list=list()
 
      satt=['modificationType', 'bindsTo']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
 
      type_attribute_list=list()
 
      satt=['intraMolecular']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 


#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma['modificationType']='SequenceModificationVocabulary'  
      ma['bindsTo']='BindingFeature'  
      ma['intraMolecular']='bool'  
      return ma

