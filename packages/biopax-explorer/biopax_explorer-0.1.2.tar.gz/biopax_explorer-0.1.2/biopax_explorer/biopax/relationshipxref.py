 
from biopax.xref import Xref
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class RelationshipXref(Xref) :


    """
    Class RelationshipXref 
    
              Definition: An xref that defines a reference to an entity in an external
      resource that does not have the same biological identity as the referring
      entity. Usage: There is currently no controlled vocabulary of relationship types
      for BioPAX, although one will be created in the future if a need develops.
      Examples: A link between a gene G in a BioPAX data collection, and the protein
      product P of that gene in an external database. This is not a unification xref
      because G and P are different biological entities (one is a gene and one is a
      protein). Another example is a relationship xref for a protein that refers to
      the Gene Ontology biological process, e.g. 'immune response,' that the protein
      is involved in.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#RelationshipXref"
        self._relationshipType=kwargs.get('relationshipType',None)  
  

##########getter
     
    def get_relationshipType(self):
        """
        Attribute _relationshipType  getter
                      Definition:A controlled vocabulary term that defines the type of relationship
      that this xref defines. Usage: There is currently no controlled vocabulary of
      relationship types for BioPAX, although one will be created in the future as the
      usage of this property increases.

                """
        return self._relationshipType  
  
##########setter
    
    @validator(value='biopax.RelationshipTypeVocabulary')  
 
    def set_relationshipType(self,value):
        self._relationshipType=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['relationshipType']
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
      ma['relationshipType']='RelationshipTypeVocabulary'  
      return ma



    def to_json(self):
        return tojson(self)
        

