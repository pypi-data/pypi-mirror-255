 
from biopax.entity import Entity
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class PhysicalEntity(Entity) :


    """
    Class PhysicalEntity 
    
              Definition: A pool of molecules or molecular complexes.   Comments: Each
      PhysicalEntity is defined by a  sequence or structure based on an
      EntityReference AND any set of Features that are given. For example,  ser46
      phosphorylated p53 is a physical entity in BioPAX defined by the p53 sequence
      and the phosphorylation feature on the serine at position 46 in the sequence.
      Features are any combination of cellular location, covalent and non-covalent
      bonds with other molecules and covalent modifications.    For a specific
      molecule to be a member of the pool it has to satisfy all of the specified
      features. Unspecified features are treated as unknowns or unneccesary. Features
      that are known to not be on the molecules should be explicitly stated with the
      "not feature" property.  A physical entity in BioPAX  never represents a
      specific molecular instance.   Physical Entity can be heterogenous and
      potentially overlap, i.e. a single molecule can be counted as a member of
      multiple pools. This makes BioPAX semantics different than regular chemical
      notation but is necessary for dealing with combinatorial complexity.   Synonyms:
      part, interactor, object, species  Examples: extracellular calcium, ser 64
      phosphorylated p53

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#PhysicalEntity"
        self._cellularLocation=kwargs.get('cellularLocation',None)  
        self._feature=kwargs.get('feature',None)  
        self._memberPhysicalEntity=kwargs.get('memberPhysicalEntity',None)  
        self._notFeature=kwargs.get('notFeature',None)  
  

##########getter
     
    def get_cellularLocation(self):
        """
        Attribute _cellularLocation  getter
                      A cellular location, e.g. 'cytoplasm'. This should reference a term in the Gene
      Ontology Cellular Component ontology. The location referred to by this property
      should be as specific as is known. If an interaction is known to occur in
      multiple locations, separate interactions (and physicalEntities) must be created
      for each different location.  If the location of a participant in a complex is
      unspecified, it may be assumed to be the same location as that of the complex.
      A molecule in two different cellular locations are considered two different
      physical entities.

                """
        return self._cellularLocation  
     
    def get_feature(self):
        """
        Attribute _feature  getter
                      Sequence features of the owner physical entity.

                """
        return self._feature  
     
    def get_memberPhysicalEntity(self):
        """
        Attribute _memberPhysicalEntity  getter
                      This property stores the members of a generic physical entity.   For
      representing homology generics a better way is to use generic entity references
      and generic features. However not all generic logic can be captured by this,
      such as complex generics or rare cases where feature cardinality is variable.
      Usages of this property should be limited to such cases.

                """
        return self._memberPhysicalEntity  
     
    def get_notFeature(self):
        """
        Attribute _notFeature  getter
                      Sequence features where the owner physical entity has a feature. If not
      specified, other potential features are not known.

                """
        return self._notFeature  
  
##########setter
    
    @validator(value='biopax.CellularLocationVocabulary')  
 
    def set_cellularLocation(self,value):
        self._cellularLocation=value  
    
    @validator(value='biopax.EntityFeature')  
 
    def set_feature(self,value):
        self._feature=value  
    
    @validator(value='biopax.PhysicalEntity')  
 
    def set_memberPhysicalEntity(self,value):
        self._memberPhysicalEntity=value  
    
    @validator(value='biopax.EntityFeature')  
 
    def set_notFeature(self,value):
        self._notFeature=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['cellularLocation', 'feature', 'memberPhysicalEntity', 'notFeature']
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
      ma['cellularLocation']='CellularLocationVocabulary'  
      ma['feature']='EntityFeature'  
      ma['memberPhysicalEntity']='PhysicalEntity'  
      ma['notFeature']='EntityFeature'  
      return ma



    def to_json(self):
        return tojson(self)
        

