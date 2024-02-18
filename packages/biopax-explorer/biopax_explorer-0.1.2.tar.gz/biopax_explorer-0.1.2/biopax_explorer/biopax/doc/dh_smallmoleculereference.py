
from biopax.utils import gen_utils
 

class smallmoleculereference_DocHelper():
  """
  Class smallmoleculereference_DocHelper

  documentation helper for smallmoleculereference
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='SmallMoleculeReference'
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
    # class SmallMoleculeReference
    dmap['SmallMoleculeReference']=dict()
    dmap['SmallMoleculeReference']['class']="""
A small molecule reference is a grouping of several small molecule entities  that have the same chemical structure.  Members can differ in celular location and bound partners. Covalent modifications of small molecules are not considered as state changes but treated as different molecules.
    """
    dmap['SmallMoleculeReference']['attribute']=dict()
  
    dmap['SmallMoleculeReference']['attribute']['structure']="""
Defines the chemical structure and other information about this molecule, using an instance of class chemicalStructure.
    """
    dmap['SmallMoleculeReference']['attribute']['chemicalFormula']="""
The chemical formula of the small molecule. Note: chemical formula can also be stored in the STRUCTURE property (in CML). In case of disagreement between the value of this property and that in the CML file, the CML value takes precedence.
    """
    dmap['SmallMoleculeReference']['attribute']['molecularWeight']="""
Defines the molecular weight of the molecule, in daltons.
    """
    dmap['SmallMoleculeReference']['attribute']['entityFeature']="""
Variable features that are observed for the entities of this entityReference - such as known PTM or methylation sites and non-covalent bonds. Note that this is an aggregate list of all known features and it does not represent a state itself.
    """
    dmap['SmallMoleculeReference']['attribute']['entityReferenceType']="""
A controlled vocabulary term that is used to describe the type of grouping such as homology or functional group.
    """
    dmap['SmallMoleculeReference']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['SmallMoleculeReference']['attribute']['memberEntityReference']="""
An entity reference that qualifies for the definition of this group. For example a member of a PFAM protein family.
    """
    dmap['SmallMoleculeReference']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['SmallMoleculeReference']['attribute']['displayName']="""
An abbreviated name for this entity, preferably a name that is short enough to be used in a visualization application to label a graphical element that represents this entity. If no short name is available, an xref may be used for this purpose by the visualization application.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['SmallMoleculeReference']['attribute']['name']="""
Synonyms for this entity.  standardName and shortName are subproperties of this property and if declared they are automatically considered as names. 

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['SmallMoleculeReference']['attribute']['standardName']="""
The preferred full name for this entity, if exists assigned by a standard nomenclature organization such as HUGO Gene Nomenclature Committee.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class SmallMoleculeReference
    dmap['SmallMoleculeReference']=dict()
    dmap['SmallMoleculeReference']['attribute']=dict()
    dmap['SmallMoleculeReference']['attribute']['structure']="ChemicalStructure"
    dmap['SmallMoleculeReference']['attribute']['chemicalFormula']="str"
    dmap['SmallMoleculeReference']['attribute']['molecularWeight']="float"
    dmap['SmallMoleculeReference']['attribute']['entityFeature']="EntityFeature"
    dmap['SmallMoleculeReference']['attribute']['entityReferenceType']="EntityReferenceTypeVocabulary"
    dmap['SmallMoleculeReference']['attribute']['evidence']="Evidence"
    dmap['SmallMoleculeReference']['attribute']['memberEntityReference']="EntityReference"
    dmap['SmallMoleculeReference']['attribute']['xref']="Xref"
    dmap['SmallMoleculeReference']['attribute']['displayName']="str"
    dmap['SmallMoleculeReference']['attribute']['name']="str"
    dmap['SmallMoleculeReference']['attribute']['standardName']="str"
  
    return dmap    