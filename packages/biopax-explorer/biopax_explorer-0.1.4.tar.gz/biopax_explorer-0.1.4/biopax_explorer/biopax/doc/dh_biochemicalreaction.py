
from biopax.utils import gen_utils
 

class biochemicalreaction_DocHelper():
  """
  Class biochemicalreaction_DocHelper

  documentation helper for biochemicalreaction
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='BiochemicalReaction'
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
    # class BiochemicalReaction
    dmap['BiochemicalReaction']=dict()
    dmap['BiochemicalReaction']['class']="""
Definition: A conversion in which molecules of one or more physicalEntity pools, undergo covalent modifications and become a member of one or more other physicalEntity pools. The substrates of biochemical reactions are defined in terms of sums of species. This is a convention in biochemistry, and, in principle, all EC reactions should be biochemical reactions.

Examples: ATP + H2O = ADP + Pi

Comment: In the example reaction above, ATP is considered to be an equilibrium mixture of several species, namely ATP4-, HATP3-, H2ATP2-, MgATP2-, MgHATP-, and Mg2ATP. Additional species may also need to be considered if other ions (e.g. Ca2+) that bind ATP are present. Similar considerations apply to ADP and to inorganic phosphate (Pi). When writing biochemical reactions, it is not necessary to attach charges to the biochemical reactants or to include ions such as H+ and Mg2+ in the equation. The reaction is written in the direction specified by the EC nomenclature system, if applicable, regardless of the physiological direction(s) in which the reaction proceeds. Polymerization reactions involving large polymers whose structure is not explicitly captured should generally be represented as unbalanced reactions in which the monomer is consumed but the polymer remains unchanged, e.g. glycogen + glucose = glycogen. A better coverage for polymerization will be developed.
    """
    dmap['BiochemicalReaction']['attribute']=dict()
  
    dmap['BiochemicalReaction']['attribute']['deltaG']="""
For biochemical reactions, this property refers to the standard transformed Gibbs energy change for a reaction written in terms of biochemical reactants (sums of species), delta-G

Since Delta-G can change based on multiple factors including ionic strength and temperature a reaction can have multiple DeltaG values.
    """
    dmap['BiochemicalReaction']['attribute']['kEQ']="""
This quantity is dimensionless and is usually a single number. The measured equilibrium constant for a biochemical reaction, encoded by the slot KEQ, is actually the apparent equilibrium constant, K'.  Concentrations in the equilibrium constant equation refer to the total concentrations of  all forms of particular biochemical reactants. For example, in the equilibrium constant equation for the biochemical reaction in which ATP is hydrolyzed to ADP and inorganic phosphate:

K' = [ADP][P<sub>i</sub>]/[ATP],

The concentration of ATP refers to the total concentration of all of the following species:

[ATP] = [ATP<sup>4-</sup>] + [HATP<sup>3-</sup>] + [H<sub>2</sub>ATP<sup>2-</sup>] + [MgATP<sup>2-</sup>] + [MgHATP<sup>-</sup>] + [Mg<sub>2</sub>ATP].

The apparent equilibrium constant is formally dimensionless, and can be kept so by inclusion of as many of the terms (1 mol/dm<sup>3</sup>) in the numerator or denominator as necessary.  It is a function of temperature (T), ionic strength (I), pH, and pMg (pMg = -log<sub>10</sub>[Mg<sup>2+</sup>]). Therefore, these quantities must be specified to be precise, and values for KEQ for biochemical reactions may be represented as 5-tuples of the form (K' T I pH pMg).  This property may have multiple values, representing different measurements for K' obtained under the different experimental conditions listed in the 5-tuple. (This definition adapted from EcoCyc)
    """
    dmap['BiochemicalReaction']['attribute']['deltaH']="""
For biochemical reactions, this property refers to the standard transformed enthalpy change for a reaction written in terms of biochemical reactants (sums of species), delta-H'<sup>o</sup>.

  delta-G'<sup>o</sup> = delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>

Units: kJ/mole

(This definition from EcoCyc)
    """
    dmap['BiochemicalReaction']['attribute']['deltaS']="""
For biochemical reactions, this property refers to the standard transformed entropy change for a reaction written in terms of biochemical reactants (sums of species), delta-S'<sup>o</sup>.

  delta-G'<sup>o</sup> = delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>

(This definition from EcoCyc)
    """
    dmap['BiochemicalReaction']['attribute']['eCNumber']="""
The unique number assigned to a reaction by the Enzyme Commission of the International Union of Biochemistry and Molecular Biology.

Note that not all biochemical reactions currently have EC numbers assigned to them.
    """
    dmap['BiochemicalReaction']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['BiochemicalReaction']['attribute']['participantStoichiometry']="""
Stoichiometry of the left and right participants.
    """
    dmap['BiochemicalReaction']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['BiochemicalReaction']['attribute']['conversionDirection']="""
This property represents the direction of the reaction. If a reaction will run in a single direction under all biological contexts then it is considered irreversible and has a direction. Otherwise it is reversible.
    """
    dmap['BiochemicalReaction']['attribute']['spontaneous']="""
Specifies whether a conversion occurs spontaneously or not. If the spontaneity is not known, the SPONTANEOUS property should be left empty.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class BiochemicalReaction
    dmap['BiochemicalReaction']=dict()
    dmap['BiochemicalReaction']['attribute']=dict()
    dmap['BiochemicalReaction']['attribute']['deltaG']="DeltaG"
    dmap['BiochemicalReaction']['attribute']['kEQ']="KPrime"
    dmap['BiochemicalReaction']['attribute']['deltaH']="float"
    dmap['BiochemicalReaction']['attribute']['deltaS']="float"
    dmap['BiochemicalReaction']['attribute']['eCNumber']="str"
    dmap['BiochemicalReaction']['attribute']['left']="PhysicalEntity"
    dmap['BiochemicalReaction']['attribute']['participantStoichiometry']="Stoichiometry"
    dmap['BiochemicalReaction']['attribute']['right']="PhysicalEntity"
    dmap['BiochemicalReaction']['attribute']['conversionDirection']="str"
    dmap['BiochemicalReaction']['attribute']['spontaneous']="bool"
  
    return dmap    