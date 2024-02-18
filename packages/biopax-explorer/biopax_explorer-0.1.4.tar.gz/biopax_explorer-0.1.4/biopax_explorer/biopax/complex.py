 
from biopax.physicalentity import PhysicalEntity
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Complex(PhysicalEntity) :


    """
    Class Complex 
    
              Definition: A physical entity whose structure is comprised of other physical
      entities bound to each other covalently or non-covalently, at least one of which
      is a macromolecule (e.g. protein, DNA, or RNA) and the Stoichiometry of the
      components are known.   Comment: Complexes must be stable enough to function as
      a biological unit; in general, the temporary association of an enzyme with its
      substrate(s) should not be considered or represented as a complex. A complex is
      the physical product of an interaction (complexAssembly) and is not itself
      considered an interaction. The boundaries on the size of complexes described by
      this class are not defined here, although possible, elements of the cell  such a
      mitochondria would typically not be described using this class (later versions
      of this ontology may include a cellularComponent class to represent these). The
      strength of binding cannot be described currently, but may be included in future
      versions of the ontology, depending on community need. Examples: Ribosome, RNA
      polymerase II. Other examples of this class include complexes of multiple
      protein monomers and complexes of proteins and small molecules.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Complex"
        self._component=kwargs.get('component',None)  
        self._componentStoichiometry=kwargs.get('componentStoichiometry',None)  
  

##########getter
     
    def get_component(self):
        """
        Attribute _component  getter
                """
        return self._component  
     
    def get_componentStoichiometry(self):
        """
        Attribute _componentStoichiometry  getter
                      The stoichiometry of components in a complex

                """
        return self._componentStoichiometry  
  
##########setter
    
    @validator(value='biopax.PhysicalEntity')  
 
    def set_component(self,value):
        self._component=value  
    
    @validator(value='biopax.Stoichiometry')  
 
    def set_componentStoichiometry(self,value):
        self._componentStoichiometry=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['component', 'componentStoichiometry']
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
      ma['component']='PhysicalEntity'  
      ma['componentStoichiometry']='Stoichiometry'  
      return ma



    def to_json(self):
        return tojson(self)
        

