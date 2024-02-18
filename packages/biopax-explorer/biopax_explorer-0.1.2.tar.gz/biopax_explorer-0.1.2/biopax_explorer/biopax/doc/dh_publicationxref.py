
from biopax.utils import gen_utils
 

class publicationxref_DocHelper():
  """
  Class publicationxref_DocHelper

  documentation helper for publicationxref
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='PublicationXref'
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
    # class PublicationXref
    dmap['PublicationXref']=dict()
    dmap['PublicationXref']['class']="""
Definition: An xref that defines a reference to a publication such as a book, journal article, web page, or software manual.
Usage:  The reference may or may not be in a database, although references to PubMed are preferred when possible. The publication should make a direct reference to the instance it is attached to. Publication xrefs should make use of PubMed IDs wherever possible. The DB property of an xref to an entry in PubMed should use the string "PubMed" and not "MEDLINE".
Examples: PubMed:10234245
    """
    dmap['PublicationXref']['attribute']=dict()
  
    dmap['PublicationXref']['attribute']['author']="""
The authors of this publication, one per property value.
    """
    dmap['PublicationXref']['attribute']['source']="""
The source  in which the reference was published, such as: a book title, or a journal title and volume and pages.
    """
    dmap['PublicationXref']['attribute']['title']="""
The title of the publication.
    """
    dmap['PublicationXref']['attribute']['url']="""
The URL at which the publication can be found, if it is available through the Web.
    """
    dmap['PublicationXref']['attribute']['year']="""
The year in which this publication was published.
    """
    dmap['PublicationXref']['attribute']['db']="""
The name of the external database to which this xref refers.
    """
    dmap['PublicationXref']['attribute']['dbVersion']="""
The version of the external database in which this xref was last known to be valid. Resources may have recommendations for referencing dataset versions. For instance, the Gene Ontology recommends listing the date the GO terms were downloaded.
    """
    dmap['PublicationXref']['attribute']['id']="""
The primary identifier in the external database of the object to which this xref refers.
    """
    dmap['PublicationXref']['attribute']['idVersion']="""
The version number of the identifier (ID). E.g. The RefSeq accession number NM_005228.3 should be split into NM_005228 as the ID and 3 as the ID-VERSION.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class PublicationXref
    dmap['PublicationXref']=dict()
    dmap['PublicationXref']['attribute']=dict()
    dmap['PublicationXref']['attribute']['author']="str"
    dmap['PublicationXref']['attribute']['source']="str"
    dmap['PublicationXref']['attribute']['title']="str"
    dmap['PublicationXref']['attribute']['url']="str"
    dmap['PublicationXref']['attribute']['year']="int"
    dmap['PublicationXref']['attribute']['db']="str"
    dmap['PublicationXref']['attribute']['dbVersion']="str"
    dmap['PublicationXref']['attribute']['id']="str"
    dmap['PublicationXref']['attribute']['idVersion']="str"
  
    return dmap    