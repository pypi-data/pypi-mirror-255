
from biopax.utils import gen_utils
 

class degradation_DocHelper():
  """
  Class degradation_DocHelper

  documentation helper for degradation
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Degradation'
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
    # class Degradation
    dmap['Degradation']=dict()
    dmap['Degradation']['class']="""
Definition: A conversion in which a pool of macromolecules are degraded into their elementary units.

Usage: This conversion always has a direction of left-to-right and is irreversible. Degraded molecules are always represented on the left, degradation products on the right. 

Comments: Degradation is a complex abstraction over multiple reactions. Although it obeys law of mass conservation and stoichiometric, the products are rarely specified since they are ubiquitous.

Example:  Degradation of a protein to amino acids.
    """
    dmap['Degradation']['attribute']=dict()
  
    dmap['Degradation']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['Degradation']['attribute']['participantStoichiometry']="""
Stoichiometry of the left and right participants.
    """
    dmap['Degradation']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['Degradation']['attribute']['conversionDirection']="""
This property represents the direction of the reaction. If a reaction will run in a single direction under all biological contexts then it is considered irreversible and has a direction. Otherwise it is reversible.
    """
    dmap['Degradation']['attribute']['spontaneous']="""
Specifies whether a conversion occurs spontaneously or not. If the spontaneity is not known, the SPONTANEOUS property should be left empty.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Degradation
    dmap['Degradation']=dict()
    dmap['Degradation']['attribute']=dict()
    dmap['Degradation']['attribute']['left']="PhysicalEntity"
    dmap['Degradation']['attribute']['participantStoichiometry']="Stoichiometry"
    dmap['Degradation']['attribute']['right']="PhysicalEntity"
    dmap['Degradation']['attribute']['conversionDirection']="str"
    dmap['Degradation']['attribute']['spontaneous']="bool"
  
    return dmap    