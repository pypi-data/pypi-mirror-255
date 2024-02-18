
from biopax.utils import gen_utils
 

class sequenceregionvocabulary_DocHelper():
  """
  Class sequenceregionvocabulary_DocHelper

  documentation helper for sequenceregionvocabulary
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='SequenceRegionVocabulary'
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
    # class SequenceRegionVocabulary
    dmap['SequenceRegionVocabulary']=dict()
    dmap['SequenceRegionVocabulary']['class']="""
Definition: A reference to a controlled vocabulary of sequence regions, such as InterPro or Sequence Ontology (SO). Homepage at http://www.sequenceontology.org/.  Browse at http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=SO
    """
    dmap['SequenceRegionVocabulary']['attribute']=dict()
  
    dmap['SequenceRegionVocabulary']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['SequenceRegionVocabulary']['attribute']['term']="""
The external controlled vocabulary term.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class SequenceRegionVocabulary
    dmap['SequenceRegionVocabulary']=dict()
    dmap['SequenceRegionVocabulary']['attribute']=dict()
    dmap['SequenceRegionVocabulary']['attribute']['xref']="Xref"
    dmap['SequenceRegionVocabulary']['attribute']['term']="str"
  
    return dmap    