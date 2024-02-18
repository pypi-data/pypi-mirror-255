
from biopax.utils import gen_utils
 

class fragmentfeature_DocHelper():
  """
  Class fragmentfeature_DocHelper

  documentation helper for fragmentfeature
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='FragmentFeature'
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
    # class FragmentFeature
    dmap['FragmentFeature']=dict()
    dmap['FragmentFeature']['class']="""
Definition: An entity feature that represents the resulting physical entity subsequent to a cleavage or degradation event. 

Usage: Fragment Feature can be used to cover multiple types of modfications to the sequence of the physical entity: 
1.    A protein with a single cleavage site that converts the protein into two fragments (e.g. pro-insulin converted to insulin and C-peptide). TODO: CV term for sequence fragment?  PSI-MI CV term for cleavage site?
2.    A protein with two cleavage sites that removes an internal sequence e.g. an intein i.e. ABC -> A
3.    Cleavage of a circular sequence e.g. a plasmid.

In the case of removal ( e.g. intron)  the fragment that is *removed* is specified in the feature location property. In the case of a "cut" (e.g. restriction enzyme cut site) the location of the cut is specified instead.
Examples: Insulin Hormone
    """
    dmap['FragmentFeature']['attribute']=dict()
  
    dmap['FragmentFeature']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['FragmentFeature']['attribute']['featureLocation']="""
Location of the feature on the sequence of the interactor.
For modification features this is the modified base or residue. For binding features this is the binding site and for fragment features this is the location of the fragment on the "base" sequence.
One feature may have more than one location, used e.g. for features which involve sequence positions close in the folded, three-dimensional state of a protein, but non-continuous along the sequence.
Small Molecules can have binding features but currently it is not possible to define the binding site on the small molecules. In those cases this property should not be specified.
    """
    dmap['FragmentFeature']['attribute']['featureLocationType']="""
A controlled vocabulary term describing the type of the sequence location of the feature such as C-Terminal or SH2 Domain.
    """
    dmap['FragmentFeature']['attribute']['memberFeature']="""
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
    # class FragmentFeature
    dmap['FragmentFeature']=dict()
    dmap['FragmentFeature']['attribute']=dict()
    dmap['FragmentFeature']['attribute']['evidence']="Evidence"
    dmap['FragmentFeature']['attribute']['featureLocation']="SequenceLocation"
    dmap['FragmentFeature']['attribute']['featureLocationType']="SequenceRegionVocabulary"
    dmap['FragmentFeature']['attribute']['memberFeature']="EntityFeature"
  
    return dmap    