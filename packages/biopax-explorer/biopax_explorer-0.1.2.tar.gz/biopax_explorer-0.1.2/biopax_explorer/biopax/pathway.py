 
from biopax.entity import Entity
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Pathway(Entity) :


    """
    Class Pathway 
    
              Definition: A set or series of interactions, often forming a network, which
      biologists have found useful to group together for organizational, historic,
      biophysical or other reasons.  Usage: Pathways can be used for demarcating any
      subnetwork of a BioPAX model. It is also possible to define a pathway without
      specifying the interactions within the pathway. In this case, the pathway
      instance could consist simply of a name and could be treated as a 'black box'.
      Pathways can also soverlap, i.e. a single interaction might belong to multiple
      pathways. Pathways can also contain sub-pathways. Pathways are continuants.
      Synonyms: network, module, cascade,   Examples: glycolysis, valine biosynthesis,
      EGFR signaling

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Pathway"
        self._organism=kwargs.get('organism',None)  
        self._pathwayComponent=kwargs.get('pathwayComponent',None)  
        self._pathwayOrder=kwargs.get('pathwayOrder',None)  
  

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
     
    def get_pathwayComponent(self):
        """
        Attribute _pathwayComponent  getter
                      The set of interactions and/or pathwaySteps in this pathway/network. Each
      instance of the pathwayStep class defines: 1) a set of interactions that
      together define a particular step in the pathway, for example a catalysis
      instance and the conversion that it catalyzes; 2) an order relationship to one
      or more other pathway steps (via the NEXT-STEP property). Note: This ordering is
      not necessarily temporal - the order described may simply represent connectivity
      between adjacent steps. Temporal ordering information should only be inferred
      from the direction of each interaction.

                """
        return self._pathwayComponent  
     
    def get_pathwayOrder(self):
        """
        Attribute _pathwayOrder  getter
                      The ordering of components (interactions and pathways) in the context of this
      pathway. This is useful to specific circular or branched pathways or orderings
      when component biochemical reactions are normally reversible, but are directed
      in the context of this pathway.

                """
        return self._pathwayOrder  
  
##########setter
    
    @validator(value='biopax.BioSource')  
 
    def set_organism(self,value):
        self._organism=value  
    
    @validator(value='biopax.Interaction')  
 
    def set_pathwayComponent(self,value):
        self._pathwayComponent=value  
    
    @validator(value='biopax.PathwayStep')  
 
    def set_pathwayOrder(self,value):
        self._pathwayOrder=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['organism', 'pathwayComponent', 'pathwayOrder']
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
      ma['pathwayComponent']='Interaction'  
      ma['pathwayOrder']='PathwayStep'  
      return ma



    def to_json(self):
        return tojson(self)
        

