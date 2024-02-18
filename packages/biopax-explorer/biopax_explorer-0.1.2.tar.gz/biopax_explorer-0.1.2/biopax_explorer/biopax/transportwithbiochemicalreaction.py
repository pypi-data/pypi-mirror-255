##generated class TransportWithBiochemicalReaction
#############################




##   Definition: A conversion interaction that is both a biochemicalReaction and a
##   transport. In transportWithBiochemicalReaction interactions, one or more of the
##   substrates changes both their location and their physical structure. Active
##   transport reactions that use ATP as an energy source fall under this category,
##   even if the only covalent change is the hydrolysis of ATP to ADP.  Rationale:
##   This class was added to support a large number of transport events in pathway
##   databases that have a biochemical reaction during the transport process. It is
##   not expected that other double inheritance subclasses will be added to the
##   ontology at the same level as this class.  Examples: In the PEP-dependent
##   phosphotransferase system, transportation of sugar into an E. coli cell is
##   accompanied by the sugar's phosphorylation as it crosses the plasma membrane.

##############################
 
##############################
 

from biopax.utils.class_utils import tostring
from biopax.utils.validate_utils import CValidateArgType,raise_error


validator = CValidateArgType(raise_error, logger=None)

@tostring
class TransportWithBiochemicalReaction :
##multiple inheritance management (['BiochemicalReaction', 'Transport'])
#no extends here, because python does not manage multiple inheritance. 
# To avoid this limitation, we select the following 
#  design pattern :
# parent attributes are directly copied
##
##########constructor
    def __init__(self, *args, **kwargs):
        #args -- tuple of anonymous arguments
        #kwargs -- dictionary of named arguments
        
        self.pk=kwargs.get('pk',None)    
        self.pop_state=kwargs.get('pop_state',None)  
        self.exhausted=kwargs.get('exhausted',None)  
 
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#TransportWithBiochemicalReaction"

##   For biochemical reactions, this property refers to the standard transformed
##   Gibbs energy change for a reaction written in terms of biochemical reactants
##   (sums of species), delta-G  Since Delta-G can change based on multiple factors
##   including ionic strength and temperature a reaction can have multiple DeltaG
##   values.

        self._deltaG=kwargs.get('deltaG',None)  
##   This quantity is dimensionless and is usually a single number. The measured
##   equilibrium constant for a biochemical reaction, encoded by the slot KEQ, is
##   actually the apparent equilibrium constant, K'.  Concentrations in the
##   equilibrium constant equation refer to the total concentrations of  all forms of
##   particular biochemical reactants. For example, in the equilibrium constant
##   equation for the biochemical reaction in which ATP is hydrolyzed to ADP and
##   inorganic phosphate:  K' = [ADP][P<sub>i</sub>]/[ATP],  The concentration of ATP
##   refers to the total concentration of all of the following species:  [ATP] =
##   [ATP<sup>4-</sup>] + [HATP<sup>3-</sup>] + [H<sub>2</sub>ATP<sup>2-</sup>] +
##   [MgATP<sup>2-</sup>] + [MgHATP<sup>-</sup>] + [Mg<sub>2</sub>ATP].  The apparent
##   equilibrium constant is formally dimensionless, and can be kept so by inclusion
##   of as many of the terms (1 mol/dm<sup>3</sup>) in the numerator or denominator
##   as necessary.  It is a function of temperature (T), ionic strength (I), pH, and
##   pMg (pMg = -log<sub>10</sub>[Mg<sup>2+</sup>]). Therefore, these quantities must
##   be specified to be precise, and values for KEQ for biochemical reactions may be
##   represented as 5-tuples of the form (K' T I pH pMg).  This property may have
##   multiple values, representing different measurements for K' obtained under the
##   different experimental conditions listed in the 5-tuple. (This definition
##   adapted from EcoCyc)

        self._kEQ=kwargs.get('kEQ',None)  
##   For biochemical reactions, this property refers to the standard transformed
##   enthalpy change for a reaction written in terms of biochemical reactants (sums
##   of species), delta-H'<sup>o</sup>.    delta-G'<sup>o</sup> =
##   delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>  Units: kJ/mole  (This definition
##   from EcoCyc)

        self._deltaH=kwargs.get('deltaH',None)  
##   For biochemical reactions, this property refers to the standard transformed
##   entropy change for a reaction written in terms of biochemical reactants (sums of
##   species), delta-S'<sup>o</sup>.    delta-G'<sup>o</sup> = delta-H'<sup>o</sup> -
##   T delta-S'<sup>o</sup>  (This definition from EcoCyc)

        self._deltaS=kwargs.get('deltaS',None)  
##   The unique number assigned to a reaction by the Enzyme Commission of the
##   International Union of Biochemistry and Molecular Biology.  Note that not all
##   biochemical reactions currently have EC numbers assigned to them.

        self._eCNumber=kwargs.get('eCNumber',None)  
  


##########getter
     
    def get_deltaG(self):
        return self._deltaG  
     
    def get_kEQ(self):
        return self._kEQ  
     
    def get_deltaH(self):
        return self._deltaH  
     
    def get_deltaS(self):
        return self._deltaS  
     
    def get_eCNumber(self):
        return self._eCNumber  
  
##########setter
    
    @validator(value='biopax.DeltaG')  
 
    def set_deltaG(self,value):
        self._deltaG=value  
    
    @validator(value='biopax.KPrime')  
 
    def set_kEQ(self,value):
        self._kEQ=value  
    
    @validator(value=float)  
 
    def set_deltaH(self,value):
        self._deltaH=value  
    
    @validator(value=float)  
 
    def set_deltaS(self,value):
        self._deltaS=value  
    
    @validator(value=str)  
 
    def set_eCNumber(self,value):
        self._eCNumber=value  
  




    def object_attributes(self):

 
      object_attribute_list=list()
 
      satt=['deltaG', 'kEQ']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
 
      type_attribute_list=list()
 
      satt=['deltaH', 'deltaS', 'eCNumber']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 


#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma['deltaG']='DeltaG'  
      ma['kEQ']='KPrime'  
      ma['deltaH']='float'  
      ma['deltaS']='float'  
      ma['eCNumber']='str'  
      return ma

