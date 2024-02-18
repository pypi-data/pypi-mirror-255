
from biopax.utils import gen_utils
 

class deltag_DocHelper():
  """
  Class deltag_DocHelper

  documentation helper for deltag
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='DeltaG'
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
    # class DeltaG
    dmap['DeltaG']=dict()
    dmap['DeltaG']['class']="""
Definition: Standard transformed Gibbs energy change for a reaction written in terms of biochemical reactants.  
Usage: Delta-G is represented as a 5-tuple of delta-G'<sup>0</sup>, temperature, ionic strength , pH, and pMg . A conversion in BioPAX may have multiple Delta-G values, representing different measurements for delta-G'<sup>0</sup> obtained under the different experimental conditions.
    """
    dmap['DeltaG']['attribute']=dict()
  
    dmap['DeltaG']['attribute']['deltaGPrime0']="""
For biochemical reactions, this property refers to the standard transformed Gibbs energy change for a reaction written in terms of biochemical reactants (sums of species), delta-G'<sup>o</sup>.

  delta-G'<sup>o</sup> = -RT lnK'
and
  delta-G'<sup>o</sup> = delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>

delta-G'<sup>o</sup> has units of kJ/mol.  Like K', it is a function of temperature (T), ionic strength (I), pH, and pMg (pMg = -log<sub>10</sub>[Mg<sup>2+</sup>]). Therefore, these quantities must be specified, and values for DELTA-G for biochemical reactions are represented as 5-tuples of the form (delta-G'<sup>o</sup> T I pH pMg).
    """
    dmap['DeltaG']['attribute']['ionicStrength']="""
The ionic strength is defined as half of the total sum of the concentration (ci) of every ionic species (i) in the solution times the square of its charge (zi). For example, the ionic strength of a 0.1 M solution of CaCl2 is 0.5 x (0.1 x 22 + 0.2 x 12) = 0.3 M
    """
    dmap['DeltaG']['attribute']['ph']="""
A measure of acidity and alkalinity of a solution that is a number on a scale on which a value of 7 represents neutrality and lower numbers indicate increasing acidity and higher numbers increasing alkalinity and on which each unit of change represents a tenfold change in acidity or alkalinity and that is the negative logarithm of the effective hydrogen-ion concentration or hydrogen-ion activity in gram equivalents per liter of the solution. (Definition from Merriam-Webster Dictionary)
    """
    dmap['DeltaG']['attribute']['pMg']="""
A measure of the concentration of magnesium (Mg) in solution. (pMg = -log<sub>10</sub>[Mg<sup>2+</sup>])
    """
    dmap['DeltaG']['attribute']['temperature']="""
Temperature in Celsius
    """
    dmap['DeltaG']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class DeltaG
    dmap['DeltaG']=dict()
    dmap['DeltaG']['attribute']=dict()
    dmap['DeltaG']['attribute']['deltaGPrime0']="float"
    dmap['DeltaG']['attribute']['ionicStrength']="float"
    dmap['DeltaG']['attribute']['ph']="float"
    dmap['DeltaG']['attribute']['pMg']="float"
    dmap['DeltaG']['attribute']['temperature']="float"
    dmap['DeltaG']['attribute']['comment']="str"
  
    return dmap    