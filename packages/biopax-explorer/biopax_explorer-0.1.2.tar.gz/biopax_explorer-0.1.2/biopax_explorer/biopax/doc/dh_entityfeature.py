
from biopax.utils import gen_utils
 

class entityfeature_DocHelper():
  """
  Class entityfeature_DocHelper

  documentation helper for entityfeature
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='EntityFeature'
    self.inst=gen_utils.define_model_instance(self.cln)
    self.tmap=self.attr_type_def()


  def classInfo(self):
    cln=self.cln
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       return m['class']
    return None
  
  def attributeNameString(self):
    cln=self.cln
    s=""
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         s+="%s\n" %(k)    
    return s

  def attributeNames(self):
    cln=self.cln
    al=[]
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         al.append(k)
    return al  

  def objectAttributeNames(self):
    cln=self.cln
    oa=self.inst.object_attributes()
    al=[]
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         if k in oa:
           al.append(k)
    return al    

  def typeAttributeNames(self):
    cln=self.cln
    ta=self.inst.type_attributes()
    al=[]
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         if k in ta:
           al.append(k)
    return al   


  def attributesInfo(self):
    cln=self.cln
    s=""
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         s+="%s:" %(k)
         s+="\n%s" %(atm[k])
    return s

  def attributeInfo(self,attn):
    cln=self.cln
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       if attn in atm.keys():
          return atm[attn]
    return None

  def attributeType(self,attn):
    cln=self.cln
    if cln in self.dmap.keys():
       m=self.tmap[cln]
       atm= m['attribute']
       if attn in atm.keys():
          return atm[attn]
    return None


  def definitions(self):
    dmap=dict()
    ####################################
    # class EntityFeature
    dmap['EntityFeature']=dict()
    dmap['EntityFeature']['class']="""
Description: A characteristic of a physical entity that can change while the entity still retains its biological identity. 

Rationale: Two phosphorylated forms of a protein are strictly speaking different chemical  molecules. It is, however, standard in biology to treat them as different states of the same entity, where the entity is loosely defined based on sequence. Entity Feature class and its subclassses captures these variable characteristics. A Physical Entity in BioPAX represents a pool of  molecules rather than an individual molecule. This is a notion imported from chemistry( See PhysicalEntity). Pools are defined by a set of Entity Features in the sense that a single molecule must have all of the features in the set in order to be considered a member of the pool. Since it is impossible to list and experimentally test all potential features for an  entity, features that are not listed in the selection criteria is neglected Pools can also be defined by the converse by specifying features  that are known to NOT exist in a specific context. As DNA, RNA and Proteins can be hierarchically organized into families based on sequence homology so can entity features. The memberFeature property allows capturing such hierarchical classifications among entity features.


Usage: Subclasses of entity feature describe most common biological instances and should be preferred whenever possible. One common usecase for instantiating  entity feature is, for describing active/inactive states of proteins where more specific feature information is not available.  

Examples: Open/close conformational state of channel proteins, "active"/"inactive" states, excited states of photoreactive groups.
    """
    dmap['EntityFeature']['attribute']=dict()
  
    dmap['EntityFeature']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['EntityFeature']['attribute']['featureLocation']="""
Location of the feature on the sequence of the interactor.
For modification features this is the modified base or residue. For binding features this is the binding site and for fragment features this is the location of the fragment on the "base" sequence.
One feature may have more than one location, used e.g. for features which involve sequence positions close in the folded, three-dimensional state of a protein, but non-continuous along the sequence.
Small Molecules can have binding features but currently it is not possible to define the binding site on the small molecules. In those cases this property should not be specified.
    """
    dmap['EntityFeature']['attribute']['featureLocationType']="""
A controlled vocabulary term describing the type of the sequence location of the feature such as C-Terminal or SH2 Domain.
    """
    dmap['EntityFeature']['attribute']['memberFeature']="""
An entity feature that belongs to this homology grouping.
These features should be of the same class of this EntityFeature
These features should be an EntityFeature of an EntityReference which is a memberEntityReference of the EntityReference of this feature.
If this set is not empty than the sequenceLocation of this feature should be non-specified.
Example: a homologous phosphorylation site across a protein family.
    """
    dmap['EntityFeature']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class EntityFeature
    dmap['EntityFeature']=dict()
    dmap['EntityFeature']['attribute']=dict()
    dmap['EntityFeature']['attribute']['evidence']="Evidence"
    dmap['EntityFeature']['attribute']['featureLocation']="SequenceLocation"
    dmap['EntityFeature']['attribute']['featureLocationType']="SequenceRegionVocabulary"
    dmap['EntityFeature']['attribute']['memberFeature']="EntityFeature"
    dmap['EntityFeature']['attribute']['comment']="str"
  
    return dmap    