
from biopax.utils import gen_utils
 

class modificationfeature_DocHelper():
  """
  Class modificationfeature_DocHelper

  documentation helper for modificationfeature
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='ModificationFeature'
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
    # class ModificationFeature
    dmap['ModificationFeature']=dict()
    dmap['ModificationFeature']['class']="""
Definition: An entity feature that represents  the covalently modified state of a dna, rna or a protein. 

Rationale: In Biology, identity of DNA, RNA and Protein entities are defined around a wildtype sequence. Covalent modifications to this basal sequence are represented using modificaton features. Since small molecules are identified based on their chemical structure, not sequence, a covalent modification to a small molecule would result in a different molecule. 

Usage: The added groups should be simple and stateless, such as phosphate or methyl groups and are captured by the modificationType controlled vocabulary. In other cases, such as covalently linked proteins, use CovalentBindingFeature instead. 

Instances: A phosphorylation on a protein, a methylation on a DNA.
    """
    dmap['ModificationFeature']['attribute']=dict()
  
    dmap['ModificationFeature']['attribute']['modificationType']="""
Description and classification of the feature.
    """
    dmap['ModificationFeature']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['ModificationFeature']['attribute']['featureLocation']="""
Location of the feature on the sequence of the interactor.
For modification features this is the modified base or residue. For binding features this is the binding site and for fragment features this is the location of the fragment on the "base" sequence.
One feature may have more than one location, used e.g. for features which involve sequence positions close in the folded, three-dimensional state of a protein, but non-continuous along the sequence.
Small Molecules can have binding features but currently it is not possible to define the binding site on the small molecules. In those cases this property should not be specified.
    """
    dmap['ModificationFeature']['attribute']['featureLocationType']="""
A controlled vocabulary term describing the type of the sequence location of the feature such as C-Terminal or SH2 Domain.
    """
    dmap['ModificationFeature']['attribute']['memberFeature']="""
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
    # class ModificationFeature
    dmap['ModificationFeature']=dict()
    dmap['ModificationFeature']['attribute']=dict()
    dmap['ModificationFeature']['attribute']['modificationType']="SequenceModificationVocabulary"
    dmap['ModificationFeature']['attribute']['evidence']="Evidence"
    dmap['ModificationFeature']['attribute']['featureLocation']="SequenceLocation"
    dmap['ModificationFeature']['attribute']['featureLocationType']="SequenceRegionVocabulary"
    dmap['ModificationFeature']['attribute']['memberFeature']="EntityFeature"
  
    return dmap    