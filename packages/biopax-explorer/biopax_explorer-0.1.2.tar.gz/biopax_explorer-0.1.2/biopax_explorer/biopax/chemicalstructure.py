 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class ChemicalStructure(UtilityClass) :


    """
    Class ChemicalStructure 
    
              Definition: The chemical structure of a small molecule.   Usage: Structure
      information is stored in the property structureData, in one of three formats:
      the CML format (see www.xml-cml.org), the SMILES format (see
      www.daylight.com/dayhtml/smiles/) or the InChI format
      (http://www.iupac.org/inchi/). The structureFormat property specifies which
      format is used.  Examples: The following SMILES string describes the structure
      of glucose-6-phosphate: 'C(OP(=O)(O)O)[CH]1([CH](O)[CH](O)[CH](O)[CH](O)O1)'.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#ChemicalStructure"
        self._structureData=kwargs.get('structureData',None)  
        self._structureFormat=kwargs.get('structureFormat',None)  
  

##########getter
     
    def get_structureData(self):
        """
        Attribute _structureData  getter
                      This property holds a string of data defining chemical structure,in one of the
      three formats:<a href ="www.xml-cml.org">CML</a>, <a href =
      "www.daylight.com/dayhtml/smiles/">SMILES</a> or <a
      href="http://www.iupac.org/inchi/">InChI</a>. If, for example,the CML format is
      used, then the value of this property is a string containing the XML encoding of
      the CML data.

                """
        return self._structureData  
     
    def get_structureFormat(self):
        """
        Attribute _structureFormat  getter
                      This property specifies which format is used to define chemical structure data.

                """
        return self._structureFormat  
  
##########setter
    
    @validator(value=str)  
 
    def set_structureData(self,value):
        self._structureData=value  
    
    @validator(value=str)  
 
    def set_structureFormat(self,value):
        self._structureFormat=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['structureData', 'structureFormat']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['structureData']='str'  
      ma['structureFormat']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

