
from biopax.utils import gen_utils
 

class entityreferencetypevocabulary_DocHelper():
  """
  Class entityreferencetypevocabulary_DocHelper

  documentation helper for entityreferencetypevocabulary
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='EntityReferenceTypeVocabulary'
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
    # class EntityReferenceTypeVocabulary
    dmap['EntityReferenceTypeVocabulary']=dict()
    dmap['EntityReferenceTypeVocabulary']['class']="""
Definiiton: A reference to a term from an entity reference group ontology. As of the writing of this documentation, there is no standard ontology of these terms, though a common type is ‘homology’.
    """
    dmap['EntityReferenceTypeVocabulary']['attribute']=dict()
  
    dmap['EntityReferenceTypeVocabulary']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['EntityReferenceTypeVocabulary']['attribute']['term']="""
The external controlled vocabulary term.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class EntityReferenceTypeVocabulary
    dmap['EntityReferenceTypeVocabulary']=dict()
    dmap['EntityReferenceTypeVocabulary']['attribute']=dict()
    dmap['EntityReferenceTypeVocabulary']['attribute']['xref']="Xref"
    dmap['EntityReferenceTypeVocabulary']['attribute']['term']="str"
  
    return dmap    