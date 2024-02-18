 
from biopax.conversion import Conversion
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class BiochemicalReaction(Conversion) :


    """
    Class BiochemicalReaction 
    
              Definition: A conversion in which molecules of one or more physicalEntity pools,
      undergo covalent modifications and become a member of one or more other
      physicalEntity pools. The substrates of biochemical reactions are defined in
      terms of sums of species. This is a convention in biochemistry, and, in
      principle, all EC reactions should be biochemical reactions.  Examples: ATP +
      H2O = ADP + Pi  Comment: In the example reaction above, ATP is considered to be
      an equilibrium mixture of several species, namely ATP4-, HATP3-, H2ATP2-,
      MgATP2-, MgHATP-, and Mg2ATP. Additional species may also need to be considered
      if other ions (e.g. Ca2+) that bind ATP are present. Similar considerations
      apply to ADP and to inorganic phosphate (Pi). When writing biochemical
      reactions, it is not necessary to attach charges to the biochemical reactants or
      to include ions such as H+ and Mg2+ in the equation. The reaction is written in
      the direction specified by the EC nomenclature system, if applicable, regardless
      of the physiological direction(s) in which the reaction proceeds. Polymerization
      reactions involving large polymers whose structure is not explicitly captured
      should generally be represented as unbalanced reactions in which the monomer is
      consumed but the polymer remains unchanged, e.g. glycogen + glucose = glycogen.
      A better coverage for polymerization will be developed.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#BiochemicalReaction"
        self._deltaG=kwargs.get('deltaG',None)  
        self._kEQ=kwargs.get('kEQ',None)  
        self._deltaH=kwargs.get('deltaH',None)  
        self._deltaS=kwargs.get('deltaS',None)  
        self._eCNumber=kwargs.get('eCNumber',None)  
  

##########getter
     
    def get_deltaG(self):
        """
        Attribute _deltaG  getter
                      For biochemical reactions, this property refers to the standard transformed
      Gibbs energy change for a reaction written in terms of biochemical reactants
      (sums of species), delta-G  Since Delta-G can change based on multiple factors
      including ionic strength and temperature a reaction can have multiple DeltaG
      values.

                """
        return self._deltaG  
     
    def get_kEQ(self):
        """
        Attribute _kEQ  getter
                      This quantity is dimensionless and is usually a single number. The measured
      equilibrium constant for a biochemical reaction, encoded by the slot KEQ, is
      actually the apparent equilibrium constant, K'.  Concentrations in the
      equilibrium constant equation refer to the total concentrations of  all forms of
      particular biochemical reactants. For example, in the equilibrium constant
      equation for the biochemical reaction in which ATP is hydrolyzed to ADP and
      inorganic phosphate:  K' = [ADP][P<sub>i</sub>]/[ATP],  The concentration of ATP
      refers to the total concentration of all of the following species:  [ATP] =
      [ATP<sup>4-</sup>] + [HATP<sup>3-</sup>] + [H<sub>2</sub>ATP<sup>2-</sup>] +
      [MgATP<sup>2-</sup>] + [MgHATP<sup>-</sup>] + [Mg<sub>2</sub>ATP].  The apparent
      equilibrium constant is formally dimensionless, and can be kept so by inclusion
      of as many of the terms (1 mol/dm<sup>3</sup>) in the numerator or denominator
      as necessary.  It is a function of temperature (T), ionic strength (I), pH, and
      pMg (pMg = -log<sub>10</sub>[Mg<sup>2+</sup>]). Therefore, these quantities must
      be specified to be precise, and values for KEQ for biochemical reactions may be
      represented as 5-tuples of the form (K' T I pH pMg).  This property may have
      multiple values, representing different measurements for K' obtained under the
      different experimental conditions listed in the 5-tuple. (This definition
      adapted from EcoCyc)

                """
        return self._kEQ  
     
    def get_deltaH(self):
        """
        Attribute _deltaH  getter
                      For biochemical reactions, this property refers to the standard transformed
      enthalpy change for a reaction written in terms of biochemical reactants (sums
      of species), delta-H'<sup>o</sup>.    delta-G'<sup>o</sup> =
      delta-H'<sup>o</sup> - T delta-S'<sup>o</sup>  Units: kJ/mole  (This definition
      from EcoCyc)

                """
        return self._deltaH  
     
    def get_deltaS(self):
        """
        Attribute _deltaS  getter
                      For biochemical reactions, this property refers to the standard transformed
      entropy change for a reaction written in terms of biochemical reactants (sums of
      species), delta-S'<sup>o</sup>.    delta-G'<sup>o</sup> = delta-H'<sup>o</sup> -
      T delta-S'<sup>o</sup>  (This definition from EcoCyc)

                """
        return self._deltaS  
     
    def get_eCNumber(self):
        """
        Attribute _eCNumber  getter
                      The unique number assigned to a reaction by the Enzyme Commission of the
      International Union of Biochemistry and Molecular Biology.  Note that not all
      biochemical reactions currently have EC numbers assigned to them.

                """
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

      object_attribute_list=super().object_attributes() 
      satt=['deltaG', 'kEQ']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['deltaH', 'deltaS', 'eCNumber']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['deltaG']='DeltaG'  
      ma['kEQ']='KPrime'  
      ma['deltaH']='float'  
      ma['deltaS']='float'  
      ma['eCNumber']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

