##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class UtilityClass() :


    """
    Class UtilityClass 
    
              Definition: This is a placeholder for classes, used for annotating the "Entity"
      and its subclasses. Mostly, these are not  an "Entity" themselves. Examples
      include references to external databases, controlled vocabularies, evidence and
      provenance.  Rationale: Utility classes are created when simple slots are
      insufficient to describe an aspect of an entity or to increase compatibility of
      this ontology with other standards.    Usage: The utilityClass class is actually
      a metaclass and is only present to organize the other helper classes under one
      class hierarchy; instances of utilityClass should never be created.

    
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
        
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#UtilityClass"
        self._comment=kwargs.get('comment',None)  
  

##########getter
     
    def get_comment(self):
        """
        Attribute _comment  getter
                      Comment on the data in the container class. This property should be used instead
      of the OWL documentation elements (rdfs:comment) for instances because
      information in 'comment' is data to be exchanged, whereas the rdfs:comment field
      is used for metadata about the structure of the BioPAX ontology.

                """
        return self._comment  
  
##########setter
    
    @validator(value=str)  
 
    def set_comment(self,value):
        self._comment=value  
  




    def object_attributes(self):

      object_attribute_list=list()
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=list()
      satt=['comment']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma['comment']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

