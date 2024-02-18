
from biopax.utils import gen_utils
 

class xref_DocHelper():
  """
  Class xref_DocHelper

  documentation helper for xref
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Xref'
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
    # class Xref
    dmap['Xref']=dict()
    dmap['Xref']['class']="""
Definition: A reference from an instance of a class in this ontology to an object in an external resource.
Rationale: Xrefs in the future can be removed in the future in favor of explicit miram links. 
Usage: For most cases one of the subclasses of xref should be used.
    """
    dmap['Xref']['attribute']=dict()
  
    dmap['Xref']['attribute']['db']="""
The name of the external database to which this xref refers.
    """
    dmap['Xref']['attribute']['dbVersion']="""
The version of the external database in which this xref was last known to be valid. Resources may have recommendations for referencing dataset versions. For instance, the Gene Ontology recommends listing the date the GO terms were downloaded.
    """
    dmap['Xref']['attribute']['id']="""
The primary identifier in the external database of the object to which this xref refers.
    """
    dmap['Xref']['attribute']['idVersion']="""
The version number of the identifier (ID). E.g. The RefSeq accession number NM_005228.3 should be split into NM_005228 as the ID and 3 as the ID-VERSION.
    """
    dmap['Xref']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Xref
    dmap['Xref']=dict()
    dmap['Xref']['attribute']=dict()
    dmap['Xref']['attribute']['db']="str"
    dmap['Xref']['attribute']['dbVersion']="str"
    dmap['Xref']['attribute']['id']="str"
    dmap['Xref']['attribute']['idVersion']="str"
    dmap['Xref']['attribute']['comment']="str"
  
    return dmap    