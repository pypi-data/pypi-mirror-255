
from biopax.utils import gen_utils
 

class cellularlocationvocabulary_DocHelper():
  """
  Class cellularlocationvocabulary_DocHelper

  documentation helper for cellularlocationvocabulary
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='CellularLocationVocabulary'
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
    # class CellularLocationVocabulary
    dmap['CellularLocationVocabulary']=dict()
    dmap['CellularLocationVocabulary']['class']="""
Definition: A reference to the Gene Ontology Cellular Component (GO CC) ontology. Homepage at http://www.geneontology.org.  Browse at http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=GO
    """
    dmap['CellularLocationVocabulary']['attribute']=dict()
  
    dmap['CellularLocationVocabulary']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['CellularLocationVocabulary']['attribute']['term']="""
The external controlled vocabulary term.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class CellularLocationVocabulary
    dmap['CellularLocationVocabulary']=dict()
    dmap['CellularLocationVocabulary']['attribute']=dict()
    dmap['CellularLocationVocabulary']['attribute']['xref']="Xref"
    dmap['CellularLocationVocabulary']['attribute']['term']="str"
  
    return dmap    