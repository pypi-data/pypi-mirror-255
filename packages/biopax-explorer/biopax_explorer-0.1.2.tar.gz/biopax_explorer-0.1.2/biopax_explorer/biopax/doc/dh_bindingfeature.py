
from biopax.utils import gen_utils
 

class bindingfeature_DocHelper():
  """
  Class bindingfeature_DocHelper

  documentation helper for bindingfeature
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='BindingFeature'
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
    # class BindingFeature
    dmap['BindingFeature']=dict()
    dmap['BindingFeature']['class']="""
Definition : An entity feature that represent the bound state of a physical entity. A pair of binding features represents a bond. 

Rationale: A physical entity in a molecular complex is considered as a new state of an entity as it is structurally and functionally different. Binding features provide facilities for describing these states. Similar to other features, a molecule can have bound and not-bound states. 

Usage: Typically, binding features are present in pairs, each describing the binding characteristic for one of the interacting physical entities. One exception is using a binding feature with no paired feature to describe any potential binding. For example, an unbound receptor can be described by using a "not-feature" property with an unpaired binding feature as its value.  BindingSiteType and featureLocation allows annotating the binding location.

IntraMolecular property should be set to "true" if the bond links two parts of the same molecule. A pair of binding features are still used where they are owned by the same physical entity. 

If the binding is due to the covalent interactions, for example in the case of lipoproteins, CovalentBindingFeature subclass should be used instead of this class.
    """
    dmap['BindingFeature']['attribute']=dict()
  
    dmap['BindingFeature']['attribute']['bindsTo']="""
A binding feature represents a "half" of the bond between two entities. This property points to another binding feature which represents the other half. The bond can be covalent or non-covalent.
    """
    dmap['BindingFeature']['attribute']['intraMolecular']="""
This flag represents whether the binding feature is within the same molecule or not. A true value implies that the entityReferences of this feature and its binding partner are the same.
    """
    dmap['BindingFeature']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['BindingFeature']['attribute']['featureLocation']="""
Location of the feature on the sequence of the interactor.
For modification features this is the modified base or residue. For binding features this is the binding site and for fragment features this is the location of the fragment on the "base" sequence.
One feature may have more than one location, used e.g. for features which involve sequence positions close in the folded, three-dimensional state of a protein, but non-continuous along the sequence.
Small Molecules can have binding features but currently it is not possible to define the binding site on the small molecules. In those cases this property should not be specified.
    """
    dmap['BindingFeature']['attribute']['featureLocationType']="""
A controlled vocabulary term describing the type of the sequence location of the feature such as C-Terminal or SH2 Domain.
    """
    dmap['BindingFeature']['attribute']['memberFeature']="""
An entity feature that belongs to this homology grouping.
These features should be of the same class of this EntityFeature
These features should be an EntityFeature of an EntityReference which is a memberEntityReference of the EntityReference of this feature.
If this set is not empty than the sequenceLocation of this feature should be non-specified.
Example: a homologous phosphorylation site across a protein family.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class BindingFeature
    dmap['BindingFeature']=dict()
    dmap['BindingFeature']['attribute']=dict()
    dmap['BindingFeature']['attribute']['bindsTo']="BindingFeature"
    dmap['BindingFeature']['attribute']['intraMolecular']="bool"
    dmap['BindingFeature']['attribute']['evidence']="Evidence"
    dmap['BindingFeature']['attribute']['featureLocation']="SequenceLocation"
    dmap['BindingFeature']['attribute']['featureLocationType']="SequenceRegionVocabulary"
    dmap['BindingFeature']['attribute']['memberFeature']="EntityFeature"
  
    return dmap    