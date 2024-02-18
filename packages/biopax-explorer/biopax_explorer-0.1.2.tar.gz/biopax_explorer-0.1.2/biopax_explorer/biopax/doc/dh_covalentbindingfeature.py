
from biopax.utils import gen_utils
 

class covalentbindingfeature_DocHelper():
  """
  Class covalentbindingfeature_DocHelper

  documentation helper for covalentbindingfeature
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='CovalentBindingFeature'
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
    # class CovalentBindingFeature
    dmap['CovalentBindingFeature']=dict()
    dmap['CovalentBindingFeature']['class']="""
Definition : An entity feature that represent the covalently bound state of  a physical entity. 

Rationale: Most frequent covalent modifications to proteins and DNA, such as phosphorylation and metylation are covered by the ModificationFeature class. In these cases, the added groups are simple and stateless therefore they can be captured by a controlled vocabulary. In other cases, such as ThiS-Thilacyl-disulfide, the covalently linked molecules are best represented as a molecular complex. CovalentBindingFeature should be used to model such covalently linked complexes.

Usage: Using this construct, it is possible to represent small molecules as a covalent complex of two other small molecules. The demarcation of small molecules is a general problem and is delegated to small molecule databases.The best practice is not to model using covalent complexes unless at least one of the participants is a protein, DNA or RNA.

Examples:
disulfide bond
UhpC + glc-6P -> Uhpc-glc-6p
acetyl-ACP -> decenoyl-ACP
charged tRNA
    """
    dmap['CovalentBindingFeature']['attribute']=dict()
  
    dmap['CovalentBindingFeature']['attribute']['modificationType']="""
Description and classification of the feature.
    """
    dmap['CovalentBindingFeature']['attribute']['bindsTo']="""
A binding feature represents a "half" of the bond between two entities. This property points to another binding feature which represents the other half. The bond can be covalent or non-covalent.
    """
    dmap['CovalentBindingFeature']['attribute']['intraMolecular']="""
This flag represents whether the binding feature is within the same molecule or not. A true value implies that the entityReferences of this feature and its binding partner are the same.
    """
    dmap['CovalentBindingFeature']['attribute']['modificationType']="""
Description and classification of the feature.
    """
    dmap['CovalentBindingFeature']['attribute']['bindsTo']="""
A binding feature represents a "half" of the bond between two entities. This property points to another binding feature which represents the other half. The bond can be covalent or non-covalent.
    """
    dmap['CovalentBindingFeature']['attribute']['intraMolecular']="""
This flag represents whether the binding feature is within the same molecule or not. A true value implies that the entityReferences of this feature and its binding partner are the same.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class CovalentBindingFeature
    dmap['CovalentBindingFeature']=dict()
    dmap['CovalentBindingFeature']['attribute']=dict()
    dmap['CovalentBindingFeature']['attribute']['modificationType']="SequenceModificationVocabulary"
    dmap['CovalentBindingFeature']['attribute']['bindsTo']="BindingFeature"
    dmap['CovalentBindingFeature']['attribute']['intraMolecular']="bool"
    dmap['CovalentBindingFeature']['attribute']['modificationType']="SequenceModificationVocabulary"
    dmap['CovalentBindingFeature']['attribute']['bindsTo']="BindingFeature"
    dmap['CovalentBindingFeature']['attribute']['intraMolecular']="bool"
  
    return dmap    