
from biopax.utils import gen_utils
 

class sequenceinterval_DocHelper():
  """
  Class sequenceinterval_DocHelper

  documentation helper for sequenceinterval
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='SequenceInterval'
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
    # class SequenceInterval
    dmap['SequenceInterval']=dict()
    dmap['SequenceInterval']['class']="""
Definition: An interval on a sequence. 
Usage: Interval is defined as an ordered pair of SequenceSites. All of the sequence from the begin site to the end site (inclusive) is described, not any subset.
    """
    dmap['SequenceInterval']['attribute']=dict()
  
    dmap['SequenceInterval']['attribute']['sequenceIntervalBegin']="""
The begin position of a sequence interval.
    """
    dmap['SequenceInterval']['attribute']['sequenceIntervalEnd']="""
The end position of a sequence interval.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class SequenceInterval
    dmap['SequenceInterval']=dict()
    dmap['SequenceInterval']['attribute']=dict()
    dmap['SequenceInterval']['attribute']['sequenceIntervalBegin']="SequenceSite"
    dmap['SequenceInterval']['attribute']['sequenceIntervalEnd']="SequenceSite"
  
    return dmap    