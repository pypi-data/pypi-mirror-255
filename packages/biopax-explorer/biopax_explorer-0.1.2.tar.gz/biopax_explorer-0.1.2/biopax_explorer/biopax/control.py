 
from biopax.interaction import Interaction
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Control(Interaction) :


    """
    Class Control 
    
              Definition: An interaction in which one entity regulates, modifies, or otherwise
      influences a continuant entity, i.e. pathway or interaction.   Usage:
      Conceptually, physical entities are involved in interactions (or events) and the
      events are controlled or modified, not the physical entities themselves. For
      example, a kinase activating a protein is a frequent event in signaling pathways
      and is usually represented as an 'activation' arrow from the kinase to the
      substrate in signaling diagrams. This is an abstraction, called "Activity Flow"
      representation,  that can be ambiguous without context. In BioPAX, this
      information should be captured as the kinase catalyzing (via an instance of the
      catalysis class) a Biochemical Reaction in which the substrate is
      phosphorylated.  Subclasses of control define types specific to the biological
      process that is being controlled and should be used instead of the generic
      "control" class when applicable.   A control can potentially have multiple
      controllers. This acts as a logical AND, i.e. both controllers are needed to
      regulate the  controlled event. Alternatively multiple controllers can control
      the same event and this acts as a logical OR, i.e. any one of them is sufficient
      to regulate the controlled event. Using this structure it is possible to
      describe arbitrary control logic using BioPAX.  Rationale: Control can be
      temporally non-atomic, for example a pathway can control another pathway in
      BioPAX.   Synonyms: regulation, mediation  Examples: A small molecule that
      inhibits a pathway by an unknown mechanism.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Control"
        self._controlled=kwargs.get('controlled',None)  
        self._controller=kwargs.get('controller',None)  
        self._controlType=kwargs.get('controlType',None)  
  

##########getter
     
    def get_controlled(self):
        """
        Attribute _controlled  getter
                      The entity that is controlled, e.g., in a biochemical reaction, the reaction is
      controlled by an enzyme. Controlled is a sub-property of participants.

                """
        return self._controlled  
     
    def get_controller(self):
        """
        Attribute _controller  getter
                      The controlling entity, e.g., in a biochemical reaction, an enzyme is the
      controlling entity of the reaction. CONTROLLER is a sub-property of
      PARTICIPANTS.

                """
        return self._controller  
     
    def get_controlType(self):
        """
        Attribute _controlType  getter
                      Defines the nature of the control relationship between the controller and the
      controlled entities.  The following terms are possible values:  ACTIVATION:
      General activation. Compounds that activate the specified enzyme activity by an
      unknown mechanism. The mechanism is defined as unknown, because either the
      mechanism has yet to be elucidated in the experimental literature, or the
      paper(s) curated thus far do not define the mechanism, and a full literature
      search has yet to be performed.  The following term can not be used in the
      catalysis class: INHIBITION: General inhibition. Compounds that inhibit the
      specified enzyme activity by an unknown mechanism. The mechanism is defined as
      unknown, because either the mechanism has yet to be elucidated in the
      experimental literature, or the paper(s) curated thus far do not define the
      mechanism, and a full literature search has yet to be performed.  The following
      terms can only be used in the modulation class (these definitions from EcoCyc):
      INHIBITION-ALLOSTERIC Allosteric inhibitors decrease the specified enzyme
      activity by binding reversibly to the enzyme and inducing a conformational
      change that decreases the affinity of the enzyme to its substrates without
      affecting its VMAX. Allosteric inhibitors can be competitive or noncompetitive
      inhibitors, therefore, those inhibition categories can be used in conjunction
      with this category.  INHIBITION-COMPETITIVE Competitive inhibitors are compounds
      that competitively inhibit the specified enzyme activity by binding reversibly
      to the enzyme and preventing the substrate from binding. Binding of the
      inhibitor and substrate are mutually exclusive because it is assumed that the
      inhibitor and substrate can both bind only to the free enzyme. A competitive
      inhibitor can either bind to the active site of the enzyme, directly excluding
      the substrate from binding there, or it can bind to another site on the enzyme,
      altering the conformation of the enzyme such that the substrate can not bind to
      the active site.  INHIBITION-IRREVERSIBLE Irreversible inhibitors are compounds
      that irreversibly inhibit the specified enzyme activity by binding to the enzyme
      and dissociating so slowly that it is considered irreversible. For example,
      alkylating agents, such as iodoacetamide, irreversibly inhibit the catalytic
      activity of some enzymes by modifying cysteine side chains.  INHIBITION-
      NONCOMPETITIVE Noncompetitive inhibitors are compounds that noncompetitively
      inhibit the specified enzyme by binding reversibly to both the free enzyme and
      to the enzyme-substrate complex. The inhibitor and substrate may be bound to the
      enzyme simultaneously and do not exclude each other. However, only the enzyme-
      substrate complex (not the enzyme-substrate-inhibitor complex) is catalytically
      active.  INHIBITION-OTHER Compounds that inhibit the specified enzyme activity
      by a mechanism that has been characterized, but that cannot be clearly
      classified as irreversible, competitive, noncompetitive, uncompetitive, or
      allosteric.  INHIBITION-UNCOMPETITIVE Uncompetitive inhibitors are compounds
      that uncompetitively inhibit the specified enzyme activity by binding reversibly
      to the enzyme-substrate complex but not to the enzyme alone.  ACTIVATION-
      NONALLOSTERIC Nonallosteric activators increase the specified enzyme activity by
      means other than allosteric.  ACTIVATION-ALLOSTERIC Allosteric activators
      increase the specified enzyme activity by binding reversibly to the enzyme and
      inducing a conformational change that increases the affinity of the enzyme to
      its substrates without affecting its VMAX.

                """
        return self._controlType  
  
##########setter
    
    @validator(value='biopax.Entity')  
 
    def set_controlled(self,value):
        self._controlled=value  
    
    @validator(value='biopax.Entity')  
 
    def set_controller(self,value):
        self._controller=value  
    
    @validator(value=str)  
 
    def set_controlType(self,value):
        enum_val=['INHIBITION', 'ACTIVATION', 'INHIBITION-ALLOSTERIC', 'INHIBITION-COMPETITIVE', 'INHIBITION-IRREVERSIBLE', 'INHIBITION-NONCOMPETITIVE', 'INHIBITION-OTHER', 'INHIBITION-UNCOMPETITIVE', 'ACTIVATION-NONALLOSTERIC', 'ACTIVATION-ALLOSTERIC']
        if value not in enum_val:
           raise Exception("value of controlType not in   ['INHIBITION', 'ACTIVATION', 'INHIBITION-ALLOSTERIC', 'INHIBITION-COMPETITIVE', 'INHIBITION-IRREVERSIBLE', 'INHIBITION-NONCOMPETITIVE', 'INHIBITION-OTHER', 'INHIBITION-UNCOMPETITIVE', 'ACTIVATION-NONALLOSTERIC', 'ACTIVATION-ALLOSTERIC']")
        self._controlType=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['controlled', 'controller']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['controlType']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['controlled']='Entity'  
      ma['controller']='Entity'  
      ma['controlType']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

