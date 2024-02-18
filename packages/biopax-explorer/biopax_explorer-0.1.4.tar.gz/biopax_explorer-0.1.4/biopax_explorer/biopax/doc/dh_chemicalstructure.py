
from biopax.utils import gen_utils
 

class chemicalstructure_DocHelper():
  """
  Class chemicalstructure_DocHelper

  documentation helper for chemicalstructure
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='ChemicalStructure'
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
    # class ChemicalStructure
    dmap['ChemicalStructure']=dict()
    dmap['ChemicalStructure']['class']="""
Definition: The chemical structure of a small molecule. 

Usage: Structure information is stored in the property structureData, in one of three formats: the CML format (see www.xml-cml.org), the SMILES format (see  www.daylight.com/dayhtml/smiles/) or the InChI format (http://www.iupac.org/inchi/). The structureFormat property specifies which format is used.

Examples: The following SMILES string describes the structure of glucose-6-phosphate:
'C(OP(=O)(O)O)[CH]1([CH](O)[CH](O)[CH](O)[CH](O)O1)'.
    """
    dmap['ChemicalStructure']['attribute']=dict()
  
    dmap['ChemicalStructure']['attribute']['structureData']="""
This property holds a string of data defining chemical structure,in one of the three formats:<a href ="www.xml-cml.org">CML</a>, <a href = "www.daylight.com/dayhtml/smiles/">SMILES</a> or <a href="http://www.iupac.org/inchi/">InChI</a>. If, for example,the CML format is used, then the value of this property is a string containing the XML encoding of the CML data.
    """
    dmap['ChemicalStructure']['attribute']['structureFormat']="""
This property specifies which format is used to define chemical structure data.
    """
    dmap['ChemicalStructure']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class ChemicalStructure
    dmap['ChemicalStructure']=dict()
    dmap['ChemicalStructure']['attribute']=dict()
    dmap['ChemicalStructure']['attribute']['structureData']="str"
    dmap['ChemicalStructure']['attribute']['structureFormat']="str"
    dmap['ChemicalStructure']['attribute']['comment']="str"
  
    return dmap    