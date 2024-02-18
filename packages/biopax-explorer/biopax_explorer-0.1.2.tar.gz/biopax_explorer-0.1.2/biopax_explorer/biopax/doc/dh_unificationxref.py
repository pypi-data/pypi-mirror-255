
from biopax.utils import gen_utils
 

class unificationxref_DocHelper():
  """
  Class unificationxref_DocHelper

  documentation helper for unificationxref
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='UnificationXref'
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
    # class UnificationXref
    dmap['UnificationXref']=dict()
    dmap['UnificationXref']['class']="""
Definition: A unification xref defines a reference to an entity in an external resource that has the same biological identity as the referring entity
Rationale: Unification xrefs are critically important for data integration. In the future they may be replaced by direct miriam links and rdf:id based identity management. 

Usage: For example, if one wished to link from a database record, C, describing a chemical compound in a BioPAX data collection to a record, C', describing the same chemical compound in an external database, one would use a unification xref since records C and C' describe the same biological identity. Generally, unification xrefs should be used whenever possible, although there are cases where they might not be useful, such as application to application data exchange.Identity of interactions can be computed based on the  identity of its participants. An xref in a protein pointing to a gene, e.g. in the LocusLink database17, would not be a unification xref since the two entities do not have the same biological identity (one is a protein, the other is a gene). Instead, this link should be a captured as a relationship xref. References to an external controlled vocabulary term within the OpenControlledVocabulary class should use a unification xref where possible (e.g. GO:0005737).
Examples: An xref in a protein instance pointing to an entry in the Swiss-Prot database, and an xref in an RNA instance pointing to the corresponding RNA sequence in the RefSeq database..
    """
    dmap['UnificationXref']['attribute']=dict()
  
    dmap['UnificationXref']['attribute']['db']="""
The name of the external database to which this xref refers.
    """
    dmap['UnificationXref']['attribute']['dbVersion']="""
The version of the external database in which this xref was last known to be valid. Resources may have recommendations for referencing dataset versions. For instance, the Gene Ontology recommends listing the date the GO terms were downloaded.
    """
    dmap['UnificationXref']['attribute']['id']="""
The primary identifier in the external database of the object to which this xref refers.
    """
    dmap['UnificationXref']['attribute']['idVersion']="""
The version number of the identifier (ID). E.g. The RefSeq accession number NM_005228.3 should be split into NM_005228 as the ID and 3 as the ID-VERSION.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class UnificationXref
    dmap['UnificationXref']=dict()
    dmap['UnificationXref']['attribute']=dict()
    dmap['UnificationXref']['attribute']['db']="str"
    dmap['UnificationXref']['attribute']['dbVersion']="str"
    dmap['UnificationXref']['attribute']['id']="str"
    dmap['UnificationXref']['attribute']['idVersion']="str"
  
    return dmap    