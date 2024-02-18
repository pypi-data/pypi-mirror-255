 
from biopax.interaction import Interaction
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class TemplateReaction(Interaction) :


    """
    Class TemplateReaction 
    
              Definiton: An interaction where a macromolecule is polymerized from a
      template macromolecule.   Rationale: This is an abstraction over multiple (not
      explicitly stated) biochemical      reactions. The ubiquitous molecules (NTP and
      amino acids) consumed are also usually     omitted. Template reaction is non-
      stoichiometric, does not obey law of      mass conservation and temporally non-
      atomic. It, however, provides a      mechanism to capture processes that are
      central to all living organisms.    Usage: Regulation of TemplateReaction, e.g.
      via a transcription factor can be      captured using
      TemplateReactionRegulation. TemplateReaction can also be      indirect  for
      example, it is not necessary to represent intermediary mRNA      for describing
      expression of a protein. It was decided to not subclass      TemplateReaction to
      subtypes such as transcription of translation for the      sake of  simplicity.
      If needed these subclasses can be added in the      future.   Examples:
      Transcription, translation, replication, reverse transcription. E.g.      DNA to
      RNA is transcription, RNA to protein is translation and DNA to      protein is
      protein expression from DNA.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#TemplateReaction"
        self._product=kwargs.get('product',None)  
        self._template=kwargs.get('template',None)  
        self._templateDirection=kwargs.get('templateDirection',None)  
  

##########getter
     
    def get_product(self):
        """
        Attribute _product  getter
                      The product of a template reaction.

                """
        return self._product  
     
    def get_template(self):
        """
        Attribute _template  getter
                      The template molecule that is used in this template reaction.

                """
        return self._template  
     
    def get_templateDirection(self):
        """
        Attribute _templateDirection  getter
                      The direction of the template reaction on the template.

                """
        return self._templateDirection  
  
##########setter
    
    @validator(value='biopax.Entity')  
 
    def set_product(self,value):
        self._product=value  
    
    @validator(value='biopax.Entity')  
 
    def set_template(self,value):
        self._template=value  
    
    @validator(value=str)  
 
    def set_templateDirection(self,value):
        enum_val=['FORWARD', 'REVERSE']
        if value not in enum_val:
           raise Exception("value of templateDirection not in   ['FORWARD', 'REVERSE']")
        self._templateDirection=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['product', 'template']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['templateDirection']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['product']='Entity'  
      ma['template']='Entity'  
      ma['templateDirection']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

