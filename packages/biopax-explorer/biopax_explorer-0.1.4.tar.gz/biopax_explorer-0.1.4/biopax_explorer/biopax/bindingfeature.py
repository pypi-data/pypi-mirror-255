 
from biopax.entityfeature import EntityFeature
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class BindingFeature(EntityFeature) :


    """
    Class BindingFeature 
    
              Definition : An entity feature that represent the bound state of a physical
      entity. A pair of binding features represents a bond.   Rationale: A physical
      entity in a molecular complex is considered as a new state of an entity as it is
      structurally and functionally different. Binding features provide facilities for
      describing these states. Similar to other features, a molecule can have bound
      and not-bound states.   Usage: Typically, binding features are present in pairs,
      each describing the binding characteristic for one of the interacting physical
      entities. One exception is using a binding feature with no paired feature to
      describe any potential binding. For example, an unbound receptor can be
      described by using a "not-feature" property with an unpaired binding feature as
      its value.  BindingSiteType and featureLocation allows annotating the binding
      location.  IntraMolecular property should be set to "true" if the bond links two
      parts of the same molecule. A pair of binding features are still used where they
      are owned by the same physical entity.   If the binding is due to the covalent
      interactions, for example in the case of lipoproteins, CovalentBindingFeature
      subclass should be used instead of this class.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#BindingFeature"
        self._bindsTo=kwargs.get('bindsTo',None)  
        self._intraMolecular=kwargs.get('intraMolecular',None)  
  

##########getter
     
    def get_bindsTo(self):
        """
        Attribute _bindsTo  getter
                      A binding feature represents a "half" of the bond between two entities. This
      property points to another binding feature which represents the other half. The
      bond can be covalent or non-covalent.

                """
        return self._bindsTo  
     
    def get_intraMolecular(self):
        """
        Attribute _intraMolecular  getter
                      This flag represents whether the binding feature is within the same molecule or
      not. A true value implies that the entityReferences of this feature and its
      binding partner are the same.

                """
        return self._intraMolecular  
  
##########setter
    
    @validator(value='biopax.BindingFeature')  
 
    def set_bindsTo(self,value):
        self._bindsTo=value  
    
    @validator(value=bool)  
 
    def set_intraMolecular(self,value):
        self._intraMolecular=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['bindsTo']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['intraMolecular']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['bindsTo']='BindingFeature'  
      ma['intraMolecular']='bool'  
      return ma



    def to_json(self):
        return tojson(self)
        

