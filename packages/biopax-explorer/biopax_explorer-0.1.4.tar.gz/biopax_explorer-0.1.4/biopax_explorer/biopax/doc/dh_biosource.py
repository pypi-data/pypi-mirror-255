
from biopax.utils import gen_utils
 

class biosource_DocHelper():
  """
  Class biosource_DocHelper

  documentation helper for biosource
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='BioSource'
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
    # class BioSource
    dmap['BioSource']=dict()
    dmap['BioSource']['class']="""
Definition: The biological source (organism, tissue or cell type) of an Entity. 

Usage: Some entities are considered source-neutral (e.g. small molecules), and the biological source of others can be deduced from their constituentss (e.g. complex, pathway).

Instances: HeLa cells, Homo sapiens, and mouse liver tissue.
    """
    dmap['BioSource']['attribute']=dict()
  
    dmap['BioSource']['attribute']['cellType']="""
A cell type, e.g. 'HeLa'. This should reference a term in a controlled vocabulary of cell types. Best practice is to refer to OBO Cell Ontology. http://www.obofoundry.org/cgi-bin/detail.cgi?id=cell
    """
    dmap['BioSource']['attribute']['tissue']="""
An external controlled vocabulary of tissue types.
    """
    dmap['BioSource']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['BioSource']['attribute']['displayName']="""
An abbreviated name for this entity, preferably a name that is short enough to be used in a visualization application to label a graphical element that represents this entity. If no short name is available, an xref may be used for this purpose by the visualization application.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['BioSource']['attribute']['name']="""
Synonyms for this entity.  standardName and shortName are subproperties of this property and if declared they are automatically considered as names. 

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['BioSource']['attribute']['standardName']="""
The preferred full name for this entity, if exists assigned by a standard nomenclature organization such as HUGO Gene Nomenclature Committee.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['BioSource']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class BioSource
    dmap['BioSource']=dict()
    dmap['BioSource']['attribute']=dict()
    dmap['BioSource']['attribute']['cellType']="CellVocabulary"
    dmap['BioSource']['attribute']['tissue']="TissueVocabulary"
    dmap['BioSource']['attribute']['xref']="Xref"
    dmap['BioSource']['attribute']['displayName']="str"
    dmap['BioSource']['attribute']['name']="str"
    dmap['BioSource']['attribute']['standardName']="str"
    dmap['BioSource']['attribute']['comment']="str"
  
    return dmap    