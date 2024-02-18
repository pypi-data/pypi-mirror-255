 
from biopax.interaction import Interaction
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Conversion(Interaction) :


    """
    Class Conversion 
    
              Definition: An interaction in which molecules of one or more PhysicalEntity
      pools are physically transformed and become a member of one or more other
      PhysicalEntity pools. Rationale: Conversion is Comments: Conversions in BioPAX
      are stoichiometric and closed world, i.e. it is assumed that all of the
      participants are listed. Both properties are due to the law of mass
      conservation. Usage: Subclasses of conversion represent different types of
      transformation reflected by the properties of different physicalEntity.
      BiochemicalReactions will change the ModificationFeatures on a PhysicalEntity,
      Transport will change the Cellular Location and ComplexAssembly will change
      BindingFeatures. Generic Conversion class should only be used when the
      modification does not fit into a any of these classes. Example: Opening of a
      voltage gated channel.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Conversion"
        self._left=kwargs.get('left',None)  
        self._participantStoichiometry=kwargs.get('participantStoichiometry',None)  
        self._right=kwargs.get('right',None)  
        self._conversionDirection=kwargs.get('conversionDirection',None)  
        self._spontaneous=kwargs.get('spontaneous',None)  
  

##########getter
     
    def get_left(self):
        """
        Attribute _left  getter
                      The participants on the left side of the conversion interaction. Since
      conversion interactions may proceed in either the left-to-right or right-to-left
      direction, occupants of the left property may be either reactants or products.
      left is a sub-property of participants.

                """
        return self._left  
     
    def get_participantStoichiometry(self):
        """
        Attribute _participantStoichiometry  getter
                      Stoichiometry of the left and right participants.

                """
        return self._participantStoichiometry  
     
    def get_right(self):
        """
        Attribute _right  getter
                      The participants on the right side of the conversion interaction. Since
      conversion interactions may proceed in either the left-to-right or right-to-left
      direction, occupants of the RIGHT property may be either reactants or products.
      RIGHT is a sub-property of PARTICIPANTS.

                """
        return self._right  
     
    def get_conversionDirection(self):
        """
        Attribute _conversionDirection  getter
                      This property represents the direction of the reaction. If a reaction will run
      in a single direction under all biological contexts then it is considered
      irreversible and has a direction. Otherwise it is reversible.

                """
        return self._conversionDirection  
     
    def get_spontaneous(self):
        """
        Attribute _spontaneous  getter
                      Specifies whether a conversion occurs spontaneously or not. If the spontaneity
      is not known, the SPONTANEOUS property should be left empty.

                """
        return self._spontaneous  
  
##########setter
    
    @validator(value='biopax.PhysicalEntity')  
 
    def set_left(self,value):
        self._left=value  
    
    @validator(value='biopax.Stoichiometry')  
 
    def set_participantStoichiometry(self,value):
        self._participantStoichiometry=value  
    
    @validator(value='biopax.PhysicalEntity')  
 
    def set_right(self,value):
        self._right=value  
    
    @validator(value=str)  
 
    def set_conversionDirection(self,value):
        self._conversionDirection=value  
    
    @validator(value=bool)  
 
    def set_spontaneous(self,value):
        self._spontaneous=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['left', 'participantStoichiometry', 'right']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['conversionDirection', 'spontaneous']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['left']='PhysicalEntity'  
      ma['participantStoichiometry']='Stoichiometry'  
      ma['right']='PhysicalEntity'  
      ma['conversionDirection']='str'  
      ma['spontaneous']='bool'  
      return ma



    def to_json(self):
        return tojson(self)
        

