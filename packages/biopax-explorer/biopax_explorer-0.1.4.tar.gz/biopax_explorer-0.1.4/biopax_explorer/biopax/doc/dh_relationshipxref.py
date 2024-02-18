
from biopax.utils import gen_utils
 

class relationshipxref_DocHelper():
  """
  Class relationshipxref_DocHelper

  documentation helper for relationshipxref
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='RelationshipXref'
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
    # class RelationshipXref
    dmap['RelationshipXref']=dict()
    dmap['RelationshipXref']['class']="""
Definition: An xref that defines a reference to an entity in an external resource that does not have the same biological identity as the referring entity.
Usage: There is currently no controlled vocabulary of relationship types for BioPAX, although one will be created in the future if a need develops.
Examples: A link between a gene G in a BioPAX data collection, and the protein product P of that gene in an external database. This is not a unification xref because G and P are different biological entities (one is a gene and one is a protein). Another example is a relationship xref for a protein that refers to the Gene Ontology biological process, e.g. 'immune response,' that the protein is involved in.
    """
    dmap['RelationshipXref']['attribute']=dict()
  
    dmap['RelationshipXref']['attribute']['relationshipType']="""
Definition:A controlled vocabulary term that defines the type of relationship that this xref defines.
Usage: There is currently no controlled vocabulary of relationship types for BioPAX, although one will be created in the future as the usage of this property increases.
    """
    dmap['RelationshipXref']['attribute']['db']="""
The name of the external database to which this xref refers.
    """
    dmap['RelationshipXref']['attribute']['dbVersion']="""
The version of the external database in which this xref was last known to be valid. Resources may have recommendations for referencing dataset versions. For instance, the Gene Ontology recommends listing the date the GO terms were downloaded.
    """
    dmap['RelationshipXref']['attribute']['id']="""
The primary identifier in the external database of the object to which this xref refers.
    """
    dmap['RelationshipXref']['attribute']['idVersion']="""
The version number of the identifier (ID). E.g. The RefSeq accession number NM_005228.3 should be split into NM_005228 as the ID and 3 as the ID-VERSION.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class RelationshipXref
    dmap['RelationshipXref']=dict()
    dmap['RelationshipXref']['attribute']=dict()
    dmap['RelationshipXref']['attribute']['relationshipType']="RelationshipTypeVocabulary"
    dmap['RelationshipXref']['attribute']['db']="str"
    dmap['RelationshipXref']['attribute']['dbVersion']="str"
    dmap['RelationshipXref']['attribute']['id']="str"
    dmap['RelationshipXref']['attribute']['idVersion']="str"
  
    return dmap    