
from biopax.utils import gen_utils
 

class experimentalformvocabulary_DocHelper():
  """
  Class experimentalformvocabulary_DocHelper

  documentation helper for experimentalformvocabulary
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='ExperimentalFormVocabulary'
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
    # class ExperimentalFormVocabulary
    dmap['ExperimentalFormVocabulary']=dict()
    dmap['ExperimentalFormVocabulary']['class']="""
Definition: A reference to the PSI Molecular Interaction ontology (MI) participant identification method (e.g. mass spectrometry), experimental role (e.g. bait, prey), experimental preparation (e.g. expression level) type. Homepage at http://www.psidev.info/.  Browse http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0002&termName=participant%20identification%20method

http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0495&termName=experimental%20role

http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0346&termName=experimental%20preparation
    """
    dmap['ExperimentalFormVocabulary']['attribute']=dict()
  
    dmap['ExperimentalFormVocabulary']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['ExperimentalFormVocabulary']['attribute']['term']="""
The external controlled vocabulary term.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class ExperimentalFormVocabulary
    dmap['ExperimentalFormVocabulary']=dict()
    dmap['ExperimentalFormVocabulary']['attribute']=dict()
    dmap['ExperimentalFormVocabulary']['attribute']['xref']="Xref"
    dmap['ExperimentalFormVocabulary']['attribute']['term']="str"
  
    return dmap    