 
from biopax.entity import Entity
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Gene(Entity) :


    """
    Class Gene 
    
              Definition: A continuant that encodes information that can be inherited through
      replication.  Rationale: Gene is an abstract continuant that can be best
      described as a "schema", a common conception commonly used by biologists to
      demark a component within genome. In BioPAX, Gene is considered a generalization
      over eukaryotic and prokaryotic genes and is used only in genetic interactions.
      Gene is often confused with DNA and RNA fragments, however, these are considered
      the physical encoding of a gene.  N.B. Gene expression regulation makes use of
      DNA and RNA physical entities and not this class. Usage: Gene should only be
      used for describing GeneticInteractions.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Gene"
        self._organism=kwargs.get('organism',None)  
  

##########getter
     
    def get_organism(self):
        """
        Attribute _organism  getter
                      An organism, e.g. 'Homo sapiens'. This is the organism that the entity is found
      in. Pathways may not have an organism associated with them, for instance,
      reference pathways from KEGG. Sequence-based entities (DNA, protein, RNA) may
      contain an xref to a sequence database that contains organism information, in
      which case the information should be consistent with the value for ORGANISM.

                """
        return self._organism  
  
##########setter
    
    @validator(value='biopax.BioSource')  
 
    def set_organism(self,value):
        self._organism=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['organism']
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
      ma['organism']='BioSource'  
      return ma



    def to_json(self):
        return tojson(self)
        

