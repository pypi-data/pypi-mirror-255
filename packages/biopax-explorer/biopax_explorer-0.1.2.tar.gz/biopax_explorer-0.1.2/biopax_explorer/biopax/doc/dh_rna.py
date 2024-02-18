
from biopax.utils import gen_utils
 

class rna_DocHelper():
  """
  Class rna_DocHelper

  documentation helper for rna
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Rna'
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
    # class Rna
    dmap['Rna']=dict()
    dmap['Rna']['class']="""
Definition: A physical entity consisting of a sequence of ribonucleotide monophosphates; a ribonucleic acid.
Usage: RNA should be used for pools of individual RNA molecules. For describing subregions on those molecules use RNARegion.
Examples: messengerRNA, microRNA, ribosomalRNA. A specific example is the let-7 microRNA.
    """
    dmap['Rna']['attribute']=dict()
  
    dmap['Rna']['attribute']['entityReference']="""
Reference entity for this physical entity.
    """
    dmap['Rna']['attribute']['cellularLocation']="""
A cellular location, e.g. 'cytoplasm'. This should reference a term in the Gene Ontology Cellular Component ontology. The location referred to by this property should be as specific as is known. If an interaction is known to occur in multiple locations, separate interactions (and physicalEntities) must be created for each different location.  If the location of a participant in a complex is unspecified, it may be assumed to be the same location as that of the complex. 

 A molecule in two different cellular locations are considered two different physical entities.
    """
    dmap['Rna']['attribute']['feature']="""
Sequence features of the owner physical entity.
    """
    dmap['Rna']['attribute']['memberPhysicalEntity']="""
This property stores the members of a generic physical entity. 

For representing homology generics a better way is to use generic entity references and generic features. However not all generic logic can be captured by this, such as complex generics or rare cases where feature cardinality is variable. Usages of this property should be limited to such cases.
    """
    dmap['Rna']['attribute']['notFeature']="""
Sequence features where the owner physical entity has a feature. If not specified, other potential features are not known.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Rna
    dmap['Rna']=dict()
    dmap['Rna']['attribute']=dict()
    dmap['Rna']['attribute']['entityReference']="EntityReference"
    dmap['Rna']['attribute']['cellularLocation']="CellularLocationVocabulary"
    dmap['Rna']['attribute']['feature']="EntityFeature"
    dmap['Rna']['attribute']['memberPhysicalEntity']="PhysicalEntity"
    dmap['Rna']['attribute']['notFeature']="EntityFeature"
  
    return dmap    