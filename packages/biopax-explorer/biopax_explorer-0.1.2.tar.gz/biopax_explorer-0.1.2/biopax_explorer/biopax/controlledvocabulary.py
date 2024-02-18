 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class ControlledVocabulary(UtilityClass) :


    """
    Class ControlledVocabulary 
    
              Definition: This class represents a term from an external controlled vocabulary
      (CV). Rationale: Controlled Vocabularies mark cases where BioPAX delegates the
      representation of a complex biological phenomena to an external controlled
      vocabulary development effort such as Gene Ontology. Each subclass of this class
      represents one such case and often has an associated "Best-Practice" external
      resource to use. See the documentation of each subclass for more specific
      information. Correct usage of controlled vocabularies are critical to data
      exchange and integration. Usage: The individuals belonging to this class must
      unambiguously refer to the source controlled vocabulary. This can be achieved in
      two manners: The xref property of this class is restricted to the unification
      xref class. It must point to the source controlled vocabulary. Alternatively the
      rdf-id of the member individuals can be set to the designated MIRIAM URN. It is
      a best practice to do both whenever possible. Although it is possible to use
      multiple unification xrefs to identify semantically identical terms across
      alternative controlled vocabularies, this is not a recommended practice as it
      might lead to maintenance issues as the controlled vocabularies change. There is
      no recommended use-case for directly instantiating this class. Please use its
      subclasses instead.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#ControlledVocabulary"
        self._xref=kwargs.get('xref',None)  
        self._term=kwargs.get('term',None)  
  

##########getter
     
    def get_xref(self):
        """
        Attribute _xref  getter
                      Values of this property define external cross-references from this entity to
      entities in external databases.

                """
        return self._xref  
     
    def get_term(self):
        """
        Attribute _term  getter
                      The external controlled vocabulary term.

                """
        return self._term  
  
##########setter
    
    @validator(value='biopax.Xref')  
 
    def set_xref(self,value):
        self._xref=value  
    
    @validator(value=str)  
 
    def set_term(self,value):
        self._term=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['xref']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['term']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['xref']='Xref'  
      ma['term']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

