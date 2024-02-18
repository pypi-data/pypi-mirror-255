 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class KPrime(UtilityClass) :


    """
    Class KPrime 
    
              Definition: The apparent equilibrium constant, K', and associated values.
      Usage: Concentrations in the equilibrium constant equation refer to the total
      concentrations of  all forms of particular biochemical reactants. For example,
      in the equilibrium constant equation for the biochemical reaction in which ATP
      is hydrolyzed to ADP and inorganic phosphate:  K' = [ADP][P<sub>i</sub>]/[ATP],
      The concentration of ATP refers to the total concentration of all of the
      following species:  [ATP] = [ATP<sup>4-</sup>] + [HATP<sup>3-</sup>] +
      [H<sub>2</sub>ATP<sup>2-</sup>] + [MgATP<sup>2-</sup>] + [MgHATP<sup>-</sup>] +
      [Mg<sub>2</sub>ATP].  The apparent equilibrium constant is formally
      dimensionless, and can be kept so by inclusion of as many of the terms (1
      mol/dm<sup>3</sup>) in the numerator or denominator as necessary.  It is a
      function of temperature (T), ionic strength (I), pH, and pMg (pMg =
      -log<sub>10</sub>[Mg<sup>2+</sup>]). Therefore, these quantities must be
      specified to be precise, and values for KEQ for biochemical reactions may be
      represented as 5-tuples of the form (K' T I pH pMg).  This property may have
      multiple values, representing different measurements for K' obtained under the
      different experimental conditions listed in the 5-tuple. (This definition
      adapted from EcoCyc)  See http://www.chem.qmul.ac.uk/iubmb/thermod/ for a
      thermodynamics tutorial.

    
    code generator : rdfobj (author F.Moreews 2023).
    
    """

    ##########constructor

    def __init__(self, *args, **kwargs):
        #args -- tuple of anonymous arguments
        #kwargs -- dictionary of named arguments
        
        self.pk=kwargs.get('pk',None)    
        self.pop_state=kwargs.get('pop_state',None)  
        self.exhausted=kwargs.get('exhausted',None)
        self.meta_label=None  
        
        super().__init__(*args, **kwargs) 
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#KPrime"
        self._ionicStrength=kwargs.get('ionicStrength',None)  
        self._kPrime=kwargs.get('kPrime',None)  
        self._ph=kwargs.get('ph',None)  
        self._pMg=kwargs.get('pMg',None)  
        self._temperature=kwargs.get('temperature',None)  
  

##########getter
     
    def get_ionicStrength(self):
        """
        Attribute _ionicStrength  getter
                      The ionic strength is defined as half of the total sum of the concentration (ci)
      of every ionic species (i) in the solution times the square of its charge (zi).
      For example, the ionic strength of a 0.1 M solution of CaCl2 is 0.5 x (0.1 x 22
      + 0.2 x 12) = 0.3 M

                """
        return self._ionicStrength  
     
    def get_kPrime(self):
        """
        Attribute _kPrime  getter
                      The apparent equilibrium constant K'. Concentrations in the equilibrium constant
      equation refer to the total concentrations of  all forms of particular
      biochemical reactants. For example, in the equilibrium constant equation for the
      biochemical reaction in which ATP is hydrolyzed to ADP and inorganic phosphate:
      K' = [ADP][P<sub>i</sub>]/[ATP],  The concentration of ATP refers to the total
      concentration of all of the following species:  [ATP] = [ATP<sup>4-</sup>] +
      [HATP<sup>3-</sup>] + [H<sub>2</sub>ATP<sup>2-</sup>] + [MgATP<sup>2-</sup>] +
      [MgHATP<sup>-</sup>] + [Mg<sub>2</sub>ATP].  The apparent equilibrium constant
      is formally dimensionless, and can be kept so by inclusion of as many of the
      terms (1 mol/dm<sup>3</sup>) in the numerator or denominator as necessary.  It
      is a function of temperature (T), ionic strength (I), pH, and pMg (pMg =
      -log<sub>10</sub>[Mg<sup>2+</sup>]). (Definition from EcoCyc)

                """
        return self._kPrime  
     
    def get_ph(self):
        """
        Attribute _ph  getter
                      A measure of acidity and alkalinity of a solution that is a number on a scale on
      which a value of 7 represents neutrality and lower numbers indicate increasing
      acidity and higher numbers increasing alkalinity and on which each unit of
      change represents a tenfold change in acidity or alkalinity and that is the
      negative logarithm of the effective hydrogen-ion concentration or hydrogen-ion
      activity in gram equivalents per liter of the solution. (Definition from
      Merriam-Webster Dictionary)

                """
        return self._ph  
     
    def get_pMg(self):
        """
        Attribute _pMg  getter
                      A measure of the concentration of magnesium (Mg) in solution. (pMg =
      -log<sub>10</sub>[Mg<sup>2+</sup>])

                """
        return self._pMg  
     
    def get_temperature(self):
        """
        Attribute _temperature  getter
                      Temperature in Celsius

                """
        return self._temperature  
  
##########setter
    
    @validator(value=float)  
 
    def set_ionicStrength(self,value):
        self._ionicStrength=value  
    
    @validator(value=float)  
 
    def set_kPrime(self,value):
        self._kPrime=value  
    
    @validator(value=float)  
 
    def set_ph(self,value):
        self._ph=value  
    
    @validator(value=float)  
 
    def set_pMg(self,value):
        self._pMg=value  
    
    @validator(value=float)  
 
    def set_temperature(self,value):
        self._temperature=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['ionicStrength', 'kPrime', 'ph', 'pMg', 'temperature']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['ionicStrength']='float'  
      ma['kPrime']='float'  
      ma['ph']='float'  
      ma['pMg']='float'  
      ma['temperature']='float'  
      return ma



    def to_json(self):
        return tojson(self)
        

