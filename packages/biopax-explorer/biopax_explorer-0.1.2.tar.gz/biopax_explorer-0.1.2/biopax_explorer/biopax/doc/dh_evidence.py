
from biopax.utils import gen_utils
 

class evidence_DocHelper():
  """
  Class evidence_DocHelper

  documentation helper for evidence
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Evidence'
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
    # class Evidence
    dmap['Evidence']=dict()
    dmap['Evidence']['class']="""
Definition: The support for a particular assertion, such as the existence of an interaction or pathway. 
Usage: At least one of confidence, evidenceCode, or experimentalForm must be instantiated when creating an evidence instance. XREF may reference a publication describing the experimental evidence using a publicationXref or may store a description of the experiment in an experimental description database using a unificationXref (if the referenced experiment is the same) or relationshipXref (if it is not identical, but similar in some way e.g. similar in protocol). Evidence is meant to provide more information than just an xref to the source paper.
Examples: A description of a molecular binding assay that was used to detect a protein-protein interaction.
    """
    dmap['Evidence']['attribute']=dict()
  
    dmap['Evidence']['attribute']['confidence']="""
Confidence in the containing instance.  Usually a statistical measure.
    """
    dmap['Evidence']['attribute']['evidenceCode']="""
A pointer to a term in an external controlled vocabulary, such as the GO, PSI-MI or BioCyc evidence codes, that describes the nature of the support, such as 'traceable author statement' or 'yeast two-hybrid'.
    """
    dmap['Evidence']['attribute']['experimentalForm']="""
The experimental forms associated with an evidence instance.
    """
    dmap['Evidence']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Evidence
    dmap['Evidence']=dict()
    dmap['Evidence']['attribute']=dict()
    dmap['Evidence']['attribute']['confidence']="Score"
    dmap['Evidence']['attribute']['evidenceCode']="EvidenceCodeVocabulary"
    dmap['Evidence']['attribute']['experimentalForm']="ExperimentalForm"
    dmap['Evidence']['attribute']['xref']="Xref"
  
    return dmap    