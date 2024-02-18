
from biopax.utils import gen_utils
 

class relationshiptypevocabulary_DocHelper():
  """
  Class relationshiptypevocabulary_DocHelper

  documentation helper for relationshiptypevocabulary
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='RelationshipTypeVocabulary'
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
    # class RelationshipTypeVocabulary
    dmap['RelationshipTypeVocabulary']=dict()
    dmap['RelationshipTypeVocabulary']['class']="""
Definition: Vocabulary for defining relationship Xref types. A reference to the PSI Molecular Interaction ontology (MI) Cross Reference type. Homepage at http://www.psidev.info/.  Browse at http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0353&termName=cross-reference%20type
    """
    dmap['RelationshipTypeVocabulary']['attribute']=dict()
  
    dmap['RelationshipTypeVocabulary']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['RelationshipTypeVocabulary']['attribute']['term']="""
The external controlled vocabulary term.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class RelationshipTypeVocabulary
    dmap['RelationshipTypeVocabulary']=dict()
    dmap['RelationshipTypeVocabulary']['attribute']=dict()
    dmap['RelationshipTypeVocabulary']['attribute']['xref']="Xref"
    dmap['RelationshipTypeVocabulary']['attribute']['term']="str"
  
    return dmap    