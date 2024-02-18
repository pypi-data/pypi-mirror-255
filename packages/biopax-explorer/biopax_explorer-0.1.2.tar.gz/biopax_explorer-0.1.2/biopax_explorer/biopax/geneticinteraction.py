 
from biopax.interaction import Interaction
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class GeneticInteraction(Interaction) :


    """
    Class GeneticInteraction 
    
              Definition : Genetic interactions between genes occur when two genetic
      perturbations (e.g. mutations) have a combined phenotypic effect not caused by
      either perturbation alone. A gene participant in a genetic interaction
      represents the gene that is perturbed. Genetic interactions are not physical
      interactions but logical (AND) relationships. Their physical manifestations can
      be complex and span an arbitarily long duration.   Rationale: Currently,  BioPAX
      provides a simple definition that can capture most genetic interactions
      described in the literature. In the future, if required, the definition can be
      extended to capture other logical relationships and different, participant
      specific phenotypes.   Example: A synthetic lethal interaction occurs when cell
      growth is possible without either gene A OR B, but not without both gene A AND
      B. If you knock out A and B together, the cell will die.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#GeneticInteraction"
        self._interactionScore=kwargs.get('interactionScore',None)  
        self._phenotype=kwargs.get('phenotype',None)  
  

##########getter
     
    def get_interactionScore(self):
        """
        Attribute _interactionScore  getter
                      The score of an interaction e.g. a genetic interaction score.

                """
        return self._interactionScore  
     
    def get_phenotype(self):
        """
        Attribute _phenotype  getter
                      The phenotype quality used to define this genetic interaction e.g. viability.

                """
        return self._phenotype  
  
##########setter
    
    @validator(value='biopax.Score')  
 
    def set_interactionScore(self,value):
        self._interactionScore=value  
    
    @validator(value='biopax.PhenotypeVocabulary')  
 
    def set_phenotype(self,value):
        self._phenotype=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['interactionScore', 'phenotype']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['interactionScore']='Score'  
      ma['phenotype']='PhenotypeVocabulary'  
      return ma



    def to_json(self):
        return tojson(self)
        

