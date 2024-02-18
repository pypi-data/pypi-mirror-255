
from biopax.utils import gen_utils
 

class dnareference_DocHelper():
  """
  Class dnareference_DocHelper

  documentation helper for dnareference
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='DnaReference'
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
    # class DnaReference
    dmap['DnaReference']=dict()
    dmap['DnaReference']['class']="""
Definition: A DNA reference is a grouping of several DNA entities that are common in sequence.  Members can differ in celular location, sequence features, SNPs, mutations and bound partners.

Comments : Note that this is not a reference gene. Genes are non-physical,stateless continuants. Their physical manifestations can span multiple DNA molecules, sometimes even across chromosomes due to regulatory regions. Similarly a gene is not necessarily made up of deoxyribonucleic acid and can be present in multiple copies ( which are different DNA regions).
    """
    dmap['DnaReference']['attribute']=dict()
  
    dmap['DnaReference']['attribute']['organism']="""
An organism, e.g. 'Homo sapiens'. This is the organism that the entity is found in. Pathways may not have an organism associated with them, for instance, reference pathways from KEGG. Sequence-based entities (DNA, protein, RNA) may contain an xref to a sequence database that contains organism information, in which case the information should be consistent with the value for ORGANISM.
    """
    dmap['DnaReference']['attribute']['subRegion']="""
The sub region of a region or nucleic acid molecule. The sub region must be wholly part of the region, not outside of it.
    """
    dmap['DnaReference']['attribute']['sequence']="""
Polymer sequence in uppercase letters. For DNA, usually A,C,G,T letters representing the nucleosides of adenine, cytosine, guanine and thymine, respectively; for RNA, usually A, C, U, G; for protein, usually the letters corresponding to the 20 letter IUPAC amino acid code.
    """
    dmap['DnaReference']['attribute']['entityFeature']="""
Variable features that are observed for the entities of this entityReference - such as known PTM or methylation sites and non-covalent bonds. Note that this is an aggregate list of all known features and it does not represent a state itself.
    """
    dmap['DnaReference']['attribute']['entityReferenceType']="""
A controlled vocabulary term that is used to describe the type of grouping such as homology or functional group.
    """
    dmap['DnaReference']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['DnaReference']['attribute']['memberEntityReference']="""
An entity reference that qualifies for the definition of this group. For example a member of a PFAM protein family.
    """
    dmap['DnaReference']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['DnaReference']['attribute']['displayName']="""
An abbreviated name for this entity, preferably a name that is short enough to be used in a visualization application to label a graphical element that represents this entity. If no short name is available, an xref may be used for this purpose by the visualization application.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['DnaReference']['attribute']['name']="""
Synonyms for this entity.  standardName and shortName are subproperties of this property and if declared they are automatically considered as names. 

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['DnaReference']['attribute']['standardName']="""
The preferred full name for this entity, if exists assigned by a standard nomenclature organization such as HUGO Gene Nomenclature Committee.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class DnaReference
    dmap['DnaReference']=dict()
    dmap['DnaReference']['attribute']=dict()
    dmap['DnaReference']['attribute']['organism']="BioSource"
    dmap['DnaReference']['attribute']['subRegion']="DnaRegionReference"
    dmap['DnaReference']['attribute']['sequence']="str"
    dmap['DnaReference']['attribute']['entityFeature']="EntityFeature"
    dmap['DnaReference']['attribute']['entityReferenceType']="EntityReferenceTypeVocabulary"
    dmap['DnaReference']['attribute']['evidence']="Evidence"
    dmap['DnaReference']['attribute']['memberEntityReference']="EntityReference"
    dmap['DnaReference']['attribute']['xref']="Xref"
    dmap['DnaReference']['attribute']['displayName']="str"
    dmap['DnaReference']['attribute']['name']="str"
    dmap['DnaReference']['attribute']['standardName']="str"
  
    return dmap    