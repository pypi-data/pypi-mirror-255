 
from biopax.entityreference import EntityReference
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class SmallMoleculeReference(EntityReference) :


    """
    Class SmallMoleculeReference 
    
              A small molecule reference is a grouping of several small molecule entities
      that have the same chemical structure.  Members can differ in celular location
      and bound partners. Covalent modifications of small molecules are not considered
      as state changes but treated as different molecules.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#SmallMoleculeReference"
        self._structure=kwargs.get('structure',None)  
        self._chemicalFormula=kwargs.get('chemicalFormula',None)  
        self._molecularWeight=kwargs.get('molecularWeight',None)  
  

##########getter
     
    def get_structure(self):
        """
        Attribute _structure  getter
                      Defines the chemical structure and other information about this molecule, using
      an instance of class chemicalStructure.

                """
        return self._structure  
     
    def get_chemicalFormula(self):
        """
        Attribute _chemicalFormula  getter
                      The chemical formula of the small molecule. Note: chemical formula can also be
      stored in the STRUCTURE property (in CML). In case of disagreement between the
      value of this property and that in the CML file, the CML value takes precedence.

                """
        return self._chemicalFormula  
     
    def get_molecularWeight(self):
        """
        Attribute _molecularWeight  getter
                      Defines the molecular weight of the molecule, in daltons.

                """
        return self._molecularWeight  
  
##########setter
    
    @validator(value='biopax.ChemicalStructure')  
 
    def set_structure(self,value):
        self._structure=value  
    
    @validator(value=str)  
 
    def set_chemicalFormula(self,value):
        self._chemicalFormula=value  
    
    @validator(value=float)  
 
    def set_molecularWeight(self,value):
        self._molecularWeight=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['structure']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['chemicalFormula', 'molecularWeight']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['structure']='ChemicalStructure'  
      ma['chemicalFormula']='str'  
      ma['molecularWeight']='float'  
      return ma



    def to_json(self):
        return tojson(self)
        

