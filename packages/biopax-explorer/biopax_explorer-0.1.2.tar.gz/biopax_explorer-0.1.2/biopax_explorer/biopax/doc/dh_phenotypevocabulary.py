
from biopax.utils import gen_utils
 

class phenotypevocabulary_DocHelper():
  """
  Class phenotypevocabulary_DocHelper

  documentation helper for phenotypevocabulary
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='PhenotypeVocabulary'
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
    # class PhenotypeVocabulary
    dmap['PhenotypeVocabulary']=dict()
    dmap['PhenotypeVocabulary']['class']="""
Definition: The phenotype measured in the experiment e.g. growth rate or viability of a cell. This is only the type, not the value e.g. for a synthetic lethal interaction, the phenotype is viability, specified by ID: PATO:0000169, "viability", not the value (specified by ID: PATO:0000718, "lethal (sensu genetics)". A single term in a phenotype controlled vocabulary can be referenced using the xref, or the PhenoXML describing the PATO EQ model phenotype description can be stored as a string in PATO-DATA.
    """
    dmap['PhenotypeVocabulary']['attribute']=dict()
  
    dmap['PhenotypeVocabulary']['attribute']['patoData']="""
The phenotype data from PATO, formatted as PhenoXML (defined at http://www.fruitfly.org/~cjm/obd/formats.html)
    """
    dmap['PhenotypeVocabulary']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['PhenotypeVocabulary']['attribute']['term']="""
The external controlled vocabulary term.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class PhenotypeVocabulary
    dmap['PhenotypeVocabulary']=dict()
    dmap['PhenotypeVocabulary']['attribute']=dict()
    dmap['PhenotypeVocabulary']['attribute']['patoData']="str"
    dmap['PhenotypeVocabulary']['attribute']['xref']="Xref"
    dmap['PhenotypeVocabulary']['attribute']['term']="str"
  
    return dmap    