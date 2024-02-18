
from biopax.utils import gen_utils
 

class transportwithbiochemicalreaction_DocHelper():
  """
  Class transportwithbiochemicalreaction_DocHelper

  documentation helper for transportwithbiochemicalreaction
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='TransportWithBiochemicalReaction'
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
    # class TransportWithBiochemicalReaction
    dmap['TransportWithBiochemicalReaction']=dict()
    dmap['TransportWithBiochemicalReaction']['class']="""
Definition: A conversion interaction that is both a biochemicalReaction and a transport. In transportWithBiochemicalReaction interactions, one or more of the substrates changes both their location and their physical structure. Active transport reactions that use ATP as an energy source fall under this category, even if the only covalent change is the hydrolysis of ATP to ADP.

Rationale: This class was added to support a large number of transport events in pathway databases that have a biochemical reaction during the transport process. It is not expected that other double inheritance subclasses will be added to the ontology at the same level as this class.

Examples: In the PEP-dependent phosphotransferase system, transportation of sugar into an E. coli cell is accompanied by the sugar's phosphorylation as it crosses the plasma membrane.
    """
    dmap['TransportWithBiochemicalReaction']['attribute']=dict()
  
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaG']="""
For biochemical reactions, this property refers to the standard transformed Gibbs energy change for a reaction written in terms of biochemical reactants (sums of species), delta-G

Since Delta-G can change based on multiple factors including ionic strength and temperature a reaction can have multiple DeltaG values.
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['kEQ']="""
This quantity is dimensionless and is usually a single number. The measured equilibrium constant for a biochemical reaction, encoded by the slot KEQ, is actually the apparent equilibrium constant, K'.  Concentrations in the equilibrium constant equation refer to the total concentrations of  all forms of particular biochemical reactants. For example, in the equilibrium constant equation for the biochemical reaction in which ATP is hydrolyzed to ADP and inorganic phosphate:

K' = [ADP][P<sub>i</sub>]/[ATP],

The concentration of ATP refers to the total concentration of all of the following species:

[ATP] = [ATP<sup>4-</sup>] + [HATP<sup>3-</sup>] + [H<sub>2</sub>ATP<sup>2-</sup>] + [MgATP<sup>2-</sup>] + [MgHATP<sup>-</sup>] + [Mg<sub>2</sub>ATP].

The apparent equilibrium constant is formally dimensionless, and can be kept so by inclusion of as many of the terms (1 mol/dm<sup>3</sup>) in the numerator or denominator as necessary.  It is a function of temperature (T), ionic strength (I), pH, and pMg (pMg = -log<sub>10</sub>[Mg<sup>2+</sup>]). Therefore, these quantities must be specified to be precise, and values for KEQ for biochemical reactions may be represented as 5-tuples of the form (K' T I pH pMg).  This property may have multiple values, representing different measurements for K' obtained under the different experimental conditions listed in the 5-tuple. (This definition adapted from EcoCyc)
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaH']="""
For biochemical reactions, this property refers to the standard transformed enthalpy change for a reaction written in terms of biochemical reactants (sums of species), delta-H'<sup>o</sup>.

  delta-G'<sup>o</sup> = delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>

Units: kJ/mole

(This definition from EcoCyc)
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaS']="""
For biochemical reactions, this property refers to the standard transformed entropy change for a reaction written in terms of biochemical reactants (sums of species), delta-S'<sup>o</sup>.

  delta-G'<sup>o</sup> = delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>

(This definition from EcoCyc)
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['eCNumber']="""
The unique number assigned to a reaction by the Enzyme Commission of the International Union of Biochemistry and Molecular Biology.

Note that not all biochemical reactions currently have EC numbers assigned to them.
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaG']="""
For biochemical reactions, this property refers to the standard transformed Gibbs energy change for a reaction written in terms of biochemical reactants (sums of species), delta-G

Since Delta-G can change based on multiple factors including ionic strength and temperature a reaction can have multiple DeltaG values.
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['kEQ']="""
This quantity is dimensionless and is usually a single number. The measured equilibrium constant for a biochemical reaction, encoded by the slot KEQ, is actually the apparent equilibrium constant, K'.  Concentrations in the equilibrium constant equation refer to the total concentrations of  all forms of particular biochemical reactants. For example, in the equilibrium constant equation for the biochemical reaction in which ATP is hydrolyzed to ADP and inorganic phosphate:

K' = [ADP][P<sub>i</sub>]/[ATP],

The concentration of ATP refers to the total concentration of all of the following species:

[ATP] = [ATP<sup>4-</sup>] + [HATP<sup>3-</sup>] + [H<sub>2</sub>ATP<sup>2-</sup>] + [MgATP<sup>2-</sup>] + [MgHATP<sup>-</sup>] + [Mg<sub>2</sub>ATP].

The apparent equilibrium constant is formally dimensionless, and can be kept so by inclusion of as many of the terms (1 mol/dm<sup>3</sup>) in the numerator or denominator as necessary.  It is a function of temperature (T), ionic strength (I), pH, and pMg (pMg = -log<sub>10</sub>[Mg<sup>2+</sup>]). Therefore, these quantities must be specified to be precise, and values for KEQ for biochemical reactions may be represented as 5-tuples of the form (K' T I pH pMg).  This property may have multiple values, representing different measurements for K' obtained under the different experimental conditions listed in the 5-tuple. (This definition adapted from EcoCyc)
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaH']="""
For biochemical reactions, this property refers to the standard transformed enthalpy change for a reaction written in terms of biochemical reactants (sums of species), delta-H'<sup>o</sup>.

  delta-G'<sup>o</sup> = delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>

Units: kJ/mole

(This definition from EcoCyc)
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaS']="""
For biochemical reactions, this property refers to the standard transformed entropy change for a reaction written in terms of biochemical reactants (sums of species), delta-S'<sup>o</sup>.

  delta-G'<sup>o</sup> = delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>

(This definition from EcoCyc)
    """
    dmap['TransportWithBiochemicalReaction']['attribute']['eCNumber']="""
The unique number assigned to a reaction by the Enzyme Commission of the International Union of Biochemistry and Molecular Biology.

Note that not all biochemical reactions currently have EC numbers assigned to them.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class TransportWithBiochemicalReaction
    dmap['TransportWithBiochemicalReaction']=dict()
    dmap['TransportWithBiochemicalReaction']['attribute']=dict()
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaG']="DeltaG"
    dmap['TransportWithBiochemicalReaction']['attribute']['kEQ']="KPrime"
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaH']="float"
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaS']="float"
    dmap['TransportWithBiochemicalReaction']['attribute']['eCNumber']="str"
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaG']="DeltaG"
    dmap['TransportWithBiochemicalReaction']['attribute']['kEQ']="KPrime"
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaH']="float"
    dmap['TransportWithBiochemicalReaction']['attribute']['deltaS']="float"
    dmap['TransportWithBiochemicalReaction']['attribute']['eCNumber']="str"
  
    return dmap    