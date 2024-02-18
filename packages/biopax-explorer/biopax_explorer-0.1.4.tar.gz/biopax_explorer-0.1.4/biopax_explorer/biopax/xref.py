 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Xref(UtilityClass) :


    """
    Class Xref 
    
              Definition: A reference from an instance of a class in this ontology to an
      object in an external resource. Rationale: Xrefs in the future can be removed in
      the future in favor of explicit miram links.  Usage: For most cases one of the
      subclasses of xref should be used.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Xref"
        self._db=kwargs.get('db',None)  
        self._dbVersion=kwargs.get('dbVersion',None)  
        self._id=kwargs.get('id',None)  
        self._idVersion=kwargs.get('idVersion',None)  
  

##########getter
     
    def get_db(self):
        """
        Attribute _db  getter
                      The name of the external database to which this xref refers.

                """
        return self._db  
     
    def get_dbVersion(self):
        """
        Attribute _dbVersion  getter
                      The version of the external database in which this xref was last known to be
      valid. Resources may have recommendations for referencing dataset versions. For
      instance, the Gene Ontology recommends listing the date the GO terms were
      downloaded.

                """
        return self._dbVersion  
     
    def get_id(self):
        """
        Attribute _id  getter
                      The primary identifier in the external database of the object to which this xref
      refers.

                """
        return self._id  
     
    def get_idVersion(self):
        """
        Attribute _idVersion  getter
                      The version number of the identifier (ID). E.g. The RefSeq accession number
      NM_005228.3 should be split into NM_005228 as the ID and 3 as the ID-VERSION.

                """
        return self._idVersion  
  
##########setter
    
    @validator(value=str)  
 
    def set_db(self,value):
        self._db=value  
    
    @validator(value=str)  
 
    def set_dbVersion(self,value):
        self._dbVersion=value  
    
    @validator(value=str)  
 
    def set_id(self,value):
        self._id=value  
    
    @validator(value=str)  
 
    def set_idVersion(self,value):
        self._idVersion=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['db', 'dbVersion', 'id', 'idVersion']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['db']='str'  
      ma['dbVersion']='str'  
      ma['id']='str'  
      ma['idVersion']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

