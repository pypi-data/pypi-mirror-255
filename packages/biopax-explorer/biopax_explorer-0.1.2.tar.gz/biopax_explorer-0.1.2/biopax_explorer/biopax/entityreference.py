 
from biopax.utilityclass import UtilityClass
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class EntityReference(UtilityClass) :


    """
    Class EntityReference 
    
              Definition: An entity reference is a grouping of several physical entities
      across different contexts and molecular states, that share common physical
      properties and often named and treated as a single entity with multiple states
      by biologists.   Rationale:   Many protein, small molecule and gene databases
      share this point of view, and such a grouping is an important prerequisite for
      interoperability with those databases. Biologists would often group different
      pools of molecules in different contexts under the same name. For example
      cytoplasmic and extracellular calcium have different effects on the cell's
      behavior, but they are still called calcium. For DNA, RNA and Proteins the
      grouping is defined based on a wildtype sequence, for small molecules it is
      defined by the chemical structure.  Usage: Entity references store the
      information common to a set of molecules in various states described in the
      BioPAX document, including database cross-references. For instance, the P53
      protein can be phosphorylated in multiple different ways. Each separate P53
      protein (pool) in a phosphorylation state would be represented as a different
      protein (child of physicalEntity) and all things common to all P53 proteins,
      including all possible phosphorylation sites, the sequence common to all of them
      and common references to protein databases containing more information about P53
      would be stored in a Entity Reference.    Comments: This grouping has three
      semantic implications:  1.  Members of different pools share many physical and
      biochemical properties. This includes their chemical structure, sequence,
      organism and set of molecules they react with. They will also share a lot of
      secondary information such as their names, functional groupings, annotation
      terms and database identifiers.  2. A small number of transitions seperates
      these pools. In other words it is relatively easy and frequent for a molecule to
      transform from one physical entity to another that belong to the same reference
      entity. For example an extracellular calcium can become cytoplasmic, and p53 can
      become phosphorylated. However no calcium virtually becomes sodium, or no p53
      becomes mdm2. In the former it is the sheer energy barrier of a nuclear
      reaction, in the latter sheer statistical improbability of synthesizing the same
      sequence without a template. If one thinks about the biochemical network as
      molecules transforming into each other, and remove edges that respond to
      transcription, translation, degradation and covalent modification of small
      molecules, each remaining component is a reference entity.  3. Some of the pools
      in the same group can overlap. p53-p@ser15 can overlap with p53-p@thr18. Most of
      the experiments in molecular biology will only check for one state variable,
      rarely multiple, and never for the all possible combinations. So almost all
      statements that refer to the state of the molecule talk about a pool that can
      overlap with other pools. However no overlaps is possible between molecules of
      different groups.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#EntityReference"
        self._entityFeature=kwargs.get('entityFeature',None)  
        self._entityReferenceType=kwargs.get('entityReferenceType',None)  
        self._evidence=kwargs.get('evidence',None)  
        self._memberEntityReference=kwargs.get('memberEntityReference',None)  
        self._xref=kwargs.get('xref',None)  
        self._displayName=kwargs.get('displayName',None)  
        self._name=kwargs.get('name',None)  
        self._standardName=kwargs.get('standardName',None)  
  

##########getter
     
    def get_entityFeature(self):
        """
        Attribute _entityFeature  getter
                      Variable features that are observed for the entities of this entityReference -
      such as known PTM or methylation sites and non-covalent bonds. Note that this is
      an aggregate list of all known features and it does not represent a state
      itself.

                """
        return self._entityFeature  
     
    def get_entityReferenceType(self):
        """
        Attribute _entityReferenceType  getter
                      A controlled vocabulary term that is used to describe the type of grouping such
      as homology or functional group.

                """
        return self._entityReferenceType  
     
    def get_evidence(self):
        """
        Attribute _evidence  getter
                      Scientific evidence supporting the existence of the entity as described.

                """
        return self._evidence  
     
    def get_memberEntityReference(self):
        """
        Attribute _memberEntityReference  getter
                      An entity reference that qualifies for the definition of this group. For example
      a member of a PFAM protein family.

                """
        return self._memberEntityReference  
     
    def get_xref(self):
        """
        Attribute _xref  getter
                      Values of this property define external cross-references from this entity to
      entities in external databases.

                """
        return self._xref  
     
    def get_displayName(self):
        """
        Attribute _displayName  getter
                      An abbreviated name for this entity, preferably a name that is short enough to
      be used in a visualization application to label a graphical element that
      represents this entity. If no short name is available, an xref may be used for
      this purpose by the visualization application.  Warning:  Subproperties of name
      are functional, that is we expect to have only one standardName and shortName
      for a given entity. If a user decides to assign a different name to standardName
      or shortName, they have to remove the old triplet from the model too. If the old
      name should be retained as a synonym a regular "name" property should also be
      introduced with the old name.

                """
        return self._displayName  
     
    def get_name(self):
        """
        Attribute _name  getter
                      Synonyms for this entity.  standardName and shortName are subproperties of this
      property and if declared they are automatically considered as names.   Warning:
      Subproperties of name are functional, that is we expect to have only one
      standardName and shortName for a given entity. If a user decides to assign a
      different name to standardName or shortName, they have to remove the old triplet
      from the model too. If the old name should be retained as a synonym a regular
      "name" property should also be introduced with the old name.

                """
        return self._name  
     
    def get_standardName(self):
        """
        Attribute _standardName  getter
                      The preferred full name for this entity, if exists assigned by a standard
      nomenclature organization such as HUGO Gene Nomenclature Committee.  Warning:
      Subproperties of name are functional, that is we expect to have only one
      standardName and shortName for a given entity. If a user decides to assign a
      different name to standardName or shortName, they have to remove the old triplet
      from the model too. If the old name should be retained as a synonym a regular
      "name" property should also be introduced with the old name.

                """
        return self._standardName  
  
##########setter
    
    @validator(value='biopax.EntityFeature')  
 
    def set_entityFeature(self,value):
        self._entityFeature=value  
    
    @validator(value='biopax.EntityReferenceTypeVocabulary')  
 
    def set_entityReferenceType(self,value):
        self._entityReferenceType=value  
    
    @validator(value='biopax.Evidence')  
 
    def set_evidence(self,value):
        self._evidence=value  
    
    @validator(value='biopax.EntityReference')  
 
    def set_memberEntityReference(self,value):
        self._memberEntityReference=value  
    
    @validator(value='biopax.Xref')  
 
    def set_xref(self,value):
        self._xref=value  
    
    @validator(value=str)  
 
    def set_displayName(self,value):
        self._displayName=value  
    
    @validator(value=str)  
 
    def set_name(self,value):
        self._name=value  
    
    @validator(value=str)  
 
    def set_standardName(self,value):
        self._standardName=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['entityFeature', 'entityReferenceType', 'evidence', 'memberEntityReference', 'xref']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['displayName', 'name', 'standardName']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['entityFeature']='EntityFeature'  
      ma['entityReferenceType']='EntityReferenceTypeVocabulary'  
      ma['evidence']='Evidence'  
      ma['memberEntityReference']='EntityReference'  
      ma['xref']='Xref'  
      ma['displayName']='str'  
      ma['name']='str'  
      ma['standardName']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

