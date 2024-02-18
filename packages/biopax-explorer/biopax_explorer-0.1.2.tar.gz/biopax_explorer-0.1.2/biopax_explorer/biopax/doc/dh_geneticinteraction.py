
from biopax.utils import gen_utils
 

class geneticinteraction_DocHelper():
  """
  Class geneticinteraction_DocHelper

  documentation helper for geneticinteraction
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='GeneticInteraction'
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
    # class GeneticInteraction
    dmap['GeneticInteraction']=dict()
    dmap['GeneticInteraction']['class']="""
Definition : Genetic interactions between genes occur when two genetic perturbations (e.g. mutations) have a combined phenotypic effect not caused by either perturbation alone. A gene participant in a genetic interaction represents the gene that is perturbed. Genetic interactions are not physical interactions but logical (AND) relationships. Their physical manifestations can be complex and span an arbitarily long duration. 

Rationale: Currently,  BioPAX provides a simple definition that can capture most genetic interactions described in the literature. In the future, if required, the definition can be extended to capture other logical relationships and different, participant specific phenotypes. 

Example: A synthetic lethal interaction occurs when cell growth is possible without either gene A OR B, but not without both gene A AND B. If you knock out A and B together, the cell will die.
    """
    dmap['GeneticInteraction']['attribute']=dict()
  
    dmap['GeneticInteraction']['attribute']['interactionScore']="""
The score of an interaction e.g. a genetic interaction score.
    """
    dmap['GeneticInteraction']['attribute']['phenotype']="""
The phenotype quality used to define this genetic interaction e.g. viability.
    """
    dmap['GeneticInteraction']['attribute']['cofactor']="""
Any cofactor(s) or coenzyme(s) required for catalysis of the conversion by the enzyme. This is a suproperty of participants.
    """
    dmap['GeneticInteraction']['attribute']['controlled']="""
The entity that is controlled, e.g., in a biochemical reaction, the reaction is controlled by an enzyme. Controlled is a sub-property of participants.
    """
    dmap['GeneticInteraction']['attribute']['controller']="""
The controlling entity, e.g., in a biochemical reaction, an enzyme is the controlling entity of the reaction. CONTROLLER is a sub-property of PARTICIPANTS.
    """
    dmap['GeneticInteraction']['attribute']['interactionType']="""
Controlled vocabulary annotating the interaction type for example, "phosphorylation reaction". This annotation is meant to be human readable and may not be suitable for computing tasks, like reasoning, that require formal vocabulary systems. For instance, this information would be useful for display on a web page or for querying a database. The PSI-MI interaction type controlled vocabulary should be used. This is browsable at: 
http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0190&termName=interaction%20type
    """
    dmap['GeneticInteraction']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['GeneticInteraction']['attribute']['participant']="""
This property lists the entities that participate in this interaction. For example, in a biochemical reaction, the participants are the union of the reactants and the products of the reaction. This property has a number of sub-properties, such as LEFT and RIGHT used in the biochemicalInteraction class. Any participant listed in a sub-property will automatically be assumed to also be in PARTICIPANTS by a number of software systems, including Protege, so this property should not contain any instances if there are instances contained in a sub-property.
    """
    dmap['GeneticInteraction']['attribute']['product']="""
The product of a template reaction.
    """
    dmap['GeneticInteraction']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['GeneticInteraction']['attribute']['template']="""
The template molecule that is used in this template reaction.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class GeneticInteraction
    dmap['GeneticInteraction']=dict()
    dmap['GeneticInteraction']['attribute']=dict()
    dmap['GeneticInteraction']['attribute']['interactionScore']="Score"
    dmap['GeneticInteraction']['attribute']['phenotype']="PhenotypeVocabulary"
    dmap['GeneticInteraction']['attribute']['cofactor']="PhysicalEntity"
    dmap['GeneticInteraction']['attribute']['controlled']="Entity"
    dmap['GeneticInteraction']['attribute']['controller']="Entity"
    dmap['GeneticInteraction']['attribute']['interactionType']="InteractionVocabulary"
    dmap['GeneticInteraction']['attribute']['left']="PhysicalEntity"
    dmap['GeneticInteraction']['attribute']['participant']="Entity"
    dmap['GeneticInteraction']['attribute']['product']="Entity"
    dmap['GeneticInteraction']['attribute']['right']="PhysicalEntity"
    dmap['GeneticInteraction']['attribute']['template']="Entity"
  
    return dmap    