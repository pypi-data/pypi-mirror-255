 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class EntityFeature(UtilityClass) :


    """
    Class EntityFeature 
    
              Description: A characteristic of a physical entity that can change while the
      entity still retains its biological identity.   Rationale: Two phosphorylated
      forms of a protein are strictly speaking different chemical  molecules. It is,
      however, standard in biology to treat them as different states of the same
      entity, where the entity is loosely defined based on sequence. Entity Feature
      class and its subclassses captures these variable characteristics. A Physical
      Entity in BioPAX represents a pool of  molecules rather than an individual
      molecule. This is a notion imported from chemistry( See PhysicalEntity). Pools
      are defined by a set of Entity Features in the sense that a single molecule must
      have all of the features in the set in order to be considered a member of the
      pool. Since it is impossible to list and experimentally test all potential
      features for an  entity, features that are not listed in the selection criteria
      is neglected Pools can also be defined by the converse by specifying features
      that are known to NOT exist in a specific context. As DNA, RNA and Proteins can
      be hierarchically organized into families based on sequence homology so can
      entity features. The memberFeature property allows capturing such hierarchical
      classifications among entity features.   Usage: Subclasses of entity feature
      describe most common biological instances and should be preferred whenever
      possible. One common usecase for instantiating  entity feature is, for
      describing active/inactive states of proteins where more specific feature
      information is not available.    Examples: Open/close conformational state of
      channel proteins, "active"/"inactive" states, excited states of photoreactive
      groups.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#EntityFeature"
        self._evidence=kwargs.get('evidence',None)  
        self._featureLocation=kwargs.get('featureLocation',None)  
        self._featureLocationType=kwargs.get('featureLocationType',None)  
        self._memberFeature=kwargs.get('memberFeature',None)  
  

##########getter
     
    def get_evidence(self):
        """
        Attribute _evidence  getter
                      Scientific evidence supporting the existence of the entity as described.

                """
        return self._evidence  
     
    def get_featureLocation(self):
        """
        Attribute _featureLocation  getter
                      Location of the feature on the sequence of the interactor. For modification
      features this is the modified base or residue. For binding features this is the
      binding site and for fragment features this is the location of the fragment on
      the "base" sequence. One feature may have more than one location, used e.g. for
      features which involve sequence positions close in the folded, three-dimensional
      state of a protein, but non-continuous along the sequence. Small Molecules can
      have binding features but currently it is not possible to define the binding
      site on the small molecules. In those cases this property should not be
      specified.

                """
        return self._featureLocation  
     
    def get_featureLocationType(self):
        """
        Attribute _featureLocationType  getter
                      A controlled vocabulary term describing the type of the sequence location of the
      feature such as C-Terminal or SH2 Domain.

                """
        return self._featureLocationType  
     
    def get_memberFeature(self):
        """
        Attribute _memberFeature  getter
                      An entity feature that belongs to this homology grouping. These features should
      be of the same class of this EntityFeature These features should be an
      EntityFeature of an EntityReference which is a memberEntityReference of the
      EntityReference of this feature. If this set is not empty than the
      sequenceLocation of this feature should be non-specified. Example: a homologous
      phosphorylation site across a protein family.

                """
        return self._memberFeature  
  
##########setter
    
    @validator(value='biopax.Evidence')  
 
    def set_evidence(self,value):
        self._evidence=value  
    
    @validator(value='biopax.SequenceLocation')  
 
    def set_featureLocation(self,value):
        self._featureLocation=value  
    
    @validator(value='biopax.SequenceRegionVocabulary')  
 
    def set_featureLocationType(self,value):
        self._featureLocationType=value  
    
    @validator(value='biopax.EntityFeature')  
 
    def set_memberFeature(self,value):
        self._memberFeature=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['evidence', 'featureLocation', 'featureLocationType', 'memberFeature']
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
      ma['evidence']='Evidence'  
      ma['featureLocation']='SequenceLocation'  
      ma['featureLocationType']='SequenceRegionVocabulary'  
      ma['memberFeature']='EntityFeature'  
      return ma



    def to_json(self):
        return tojson(self)
        

