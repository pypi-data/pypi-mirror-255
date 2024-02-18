
from biopax.utils import gen_utils
 

class sequencesite_DocHelper():
  """
  Class sequencesite_DocHelper

  documentation helper for sequencesite
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='SequenceSite'
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
    # class SequenceSite
    dmap['SequenceSite']=dict()
    dmap['SequenceSite']['class']="""
Definition: Describes a site on a sequence, i.e. the position of a single nucleotide or amino acid.
Usage: A sequence site is always defined based on the reference sequence of the owning entity. For DNARegion and RNARegion it is relative to the region itself not the genome or full RNA molecule.
    """
    dmap['SequenceSite']['attribute']=dict()
  
    dmap['SequenceSite']['attribute']['positionStatus']="""
The confidence status of the sequence position. This could be:
EQUAL: The SEQUENCE-POSITION is known to be at the SEQUENCE-POSITION.
GREATER-THAN: The site is greater than the SEQUENCE-POSITION.
LESS-THAN: The site is less than the SEQUENCE-POSITION.
    """
    dmap['SequenceSite']['attribute']['sequencePosition']="""
The integer listed gives the position. The first base or amino acid is position 1. In combination with the numeric value, the property 'POSITION-STATUS' allows to express fuzzy positions, e.g. 'less than 4'.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class SequenceSite
    dmap['SequenceSite']=dict()
    dmap['SequenceSite']['attribute']=dict()
    dmap['SequenceSite']['attribute']['positionStatus']="str"
    dmap['SequenceSite']['attribute']['sequencePosition']="int"
  
    return dmap    