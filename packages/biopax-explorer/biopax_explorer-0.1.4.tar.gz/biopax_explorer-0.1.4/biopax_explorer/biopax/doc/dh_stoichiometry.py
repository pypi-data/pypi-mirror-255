
from biopax.utils import gen_utils
 

class stoichiometry_DocHelper():
  """
  Class stoichiometry_DocHelper

  documentation helper for stoichiometry
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Stoichiometry'
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
    # class Stoichiometry
    dmap['Stoichiometry']=dict()
    dmap['Stoichiometry']['class']="""
Definition: Stoichiometric coefficient of a physical entity in the context of a conversion or complex.
Usage: For each participating element there must be 0 or 1 stoichiometry element. A non-existing stoichiometric element is treated as unknown.
This is an n-ary bridge for left, right and component properties. Relative stoichiometries ( e.g n, n+1) often used for describing polymerization is not supported.
    """
    dmap['Stoichiometry']['attribute']=dict()
  
    dmap['Stoichiometry']['attribute']['physicalEntity']="""
The physical entity to be annotated with stoichiometry.
    """
    dmap['Stoichiometry']['attribute']['stoichiometricCoefficient']="""
Stoichiometric coefficient for one of the entities in an interaction or complex. This value can be any rational number. Generic values such as "n" or "n+1" should not be used - polymers are currently not covered.
    """
    dmap['Stoichiometry']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Stoichiometry
    dmap['Stoichiometry']=dict()
    dmap['Stoichiometry']['attribute']=dict()
    dmap['Stoichiometry']['attribute']['physicalEntity']="PhysicalEntity"
    dmap['Stoichiometry']['attribute']['stoichiometricCoefficient']="float"
    dmap['Stoichiometry']['attribute']['comment']="str"
  
    return dmap    