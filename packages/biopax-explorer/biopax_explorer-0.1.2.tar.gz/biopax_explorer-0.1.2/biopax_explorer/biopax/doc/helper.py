import textwrap

#utilities to manipulate the doc classes 

 
 
from biopax.doc.dh_templatereaction import templatereaction_DocHelper
 
 
from biopax.doc.dh_provenance import provenance_DocHelper
 
 
from biopax.doc.dh_covalentbindingfeature import covalentbindingfeature_DocHelper
 
 
from biopax.doc.dh_relationshiptypevocabulary import relationshiptypevocabulary_DocHelper
 
 
from biopax.doc.dh_entityreference import entityreference_DocHelper
 
 
from biopax.doc.dh_dna import dna_DocHelper
 
 
from biopax.doc.dh_molecularinteraction import molecularinteraction_DocHelper
 
 
from biopax.doc.dh_score import score_DocHelper
 
 
from biopax.doc.dh_rnareference import rnareference_DocHelper
 
 
from biopax.doc.dh_templatereactionregulation import templatereactionregulation_DocHelper
 
 
from biopax.doc.dh_complex import complex_DocHelper
 
 
from biopax.doc.dh_smallmolecule import smallmolecule_DocHelper
 
 
from biopax.doc.dh_experimentalformvocabulary import experimentalformvocabulary_DocHelper
 
 
from biopax.doc.dh_sequencelocation import sequencelocation_DocHelper
 
 
from biopax.doc.dh_smallmoleculereference import smallmoleculereference_DocHelper
 
 
from biopax.doc.dh_transport import transport_DocHelper
 
 
from biopax.doc.dh_biosource import biosource_DocHelper
 
 
from biopax.doc.dh_tissuevocabulary import tissuevocabulary_DocHelper
 
 
from biopax.doc.dh_complexassembly import complexassembly_DocHelper
 
 
from biopax.doc.dh_interactionvocabulary import interactionvocabulary_DocHelper
 
 
from biopax.doc.dh_control import control_DocHelper
 
 
from biopax.doc.dh_transportwithbiochemicalreaction import transportwithbiochemicalreaction_DocHelper
 
 
from biopax.doc.dh_sequencesite import sequencesite_DocHelper
 
 
from biopax.doc.dh_protein import protein_DocHelper
 
 
from biopax.doc.dh_interaction import interaction_DocHelper
 
 
from biopax.doc.dh_sequenceregionvocabulary import sequenceregionvocabulary_DocHelper
 
 
from biopax.doc.dh_biochemicalpathwaystep import biochemicalpathwaystep_DocHelper
 
 
from biopax.doc.dh_entityreferencetypevocabulary import entityreferencetypevocabulary_DocHelper
 
 
from biopax.doc.dh_degradation import degradation_DocHelper
 
 
from biopax.doc.dh_proteinreference import proteinreference_DocHelper
 
 
from biopax.doc.dh_sequencemodificationvocabulary import sequencemodificationvocabulary_DocHelper
 
 
from biopax.doc.dh_catalysis import catalysis_DocHelper
 
 
from biopax.doc.dh_rnaregionreference import rnaregionreference_DocHelper
 
 
from biopax.doc.dh_physicalentity import physicalentity_DocHelper
 
 
from biopax.doc.dh_rna import rna_DocHelper
 
 
from biopax.doc.dh_evidence import evidence_DocHelper
 
 
from biopax.doc.dh_pathwaystep import pathwaystep_DocHelper
 
 
from biopax.doc.dh_bindingfeature import bindingfeature_DocHelper
 
 
from biopax.doc.dh_dnaregion import dnaregion_DocHelper
 
 
from biopax.doc.dh_stoichiometry import stoichiometry_DocHelper
 
 
from biopax.doc.dh_pathway import pathway_DocHelper
 
 
from biopax.doc.dh_cellvocabulary import cellvocabulary_DocHelper
 
 
from biopax.doc.dh_publicationxref import publicationxref_DocHelper
 
 
from biopax.doc.dh_conversion import conversion_DocHelper
 
 
from biopax.doc.dh_relationshipxref import relationshipxref_DocHelper
 
 
from biopax.doc.dh_sequenceinterval import sequenceinterval_DocHelper
 
 
from biopax.doc.dh_kprime import kprime_DocHelper
 
 
from biopax.doc.dh_gene import gene_DocHelper
 
 
from biopax.doc.dh_experimentalform import experimentalform_DocHelper
 
 
from biopax.doc.dh_controlledvocabulary import controlledvocabulary_DocHelper
 
 
from biopax.doc.dh_modificationfeature import modificationfeature_DocHelper
 
 
from biopax.doc.dh_geneticinteraction import geneticinteraction_DocHelper
 
 
from biopax.doc.dh_biochemicalreaction import biochemicalreaction_DocHelper
 
 
from biopax.doc.dh_dnareference import dnareference_DocHelper
 
 
from biopax.doc.dh_dnaregionreference import dnaregionreference_DocHelper
 
 
from biopax.doc.dh_rnaregion import rnaregion_DocHelper
 
 
from biopax.doc.dh_cellularlocationvocabulary import cellularlocationvocabulary_DocHelper
 
 
from biopax.doc.dh_modulation import modulation_DocHelper
 
 
from biopax.doc.dh_xref import xref_DocHelper
 
 
from biopax.doc.dh_chemicalstructure import chemicalstructure_DocHelper
 
 
from biopax.doc.dh_fragmentfeature import fragmentfeature_DocHelper
 
 
from biopax.doc.dh_deltag import deltag_DocHelper
 
 
from biopax.doc.dh_unificationxref import unificationxref_DocHelper
 
 
from biopax.doc.dh_evidencecodevocabulary import evidencecodevocabulary_DocHelper
 
 
from biopax.doc.dh_phenotypevocabulary import phenotypevocabulary_DocHelper
 
 
from biopax.doc.dh_entityfeature import entityfeature_DocHelper
 
 
from biopax.doc.dh_utilityclass import utilityclass_DocHelper
 
 
from biopax.doc.dh_entity import entity_DocHelper
 
 
  

def entries():
      cl=list()
      cl.append("TemplateReaction")
      cl.append("Provenance")
      cl.append("CovalentBindingFeature")
      cl.append("RelationshipTypeVocabulary")
      cl.append("EntityReference")
      cl.append("Dna")
      cl.append("MolecularInteraction")
      cl.append("Score")
      cl.append("RnaReference")
      cl.append("TemplateReactionRegulation")
      cl.append("Complex")
      cl.append("SmallMolecule")
      cl.append("ExperimentalFormVocabulary")
      cl.append("SequenceLocation")
      cl.append("SmallMoleculeReference")
      cl.append("Transport")
      cl.append("BioSource")
      cl.append("TissueVocabulary")
      cl.append("ComplexAssembly")
      cl.append("InteractionVocabulary")
      cl.append("Control")
      cl.append("TransportWithBiochemicalReaction")
      cl.append("SequenceSite")
      cl.append("Protein")
      cl.append("Interaction")
      cl.append("SequenceRegionVocabulary")
      cl.append("BiochemicalPathwayStep")
      cl.append("EntityReferenceTypeVocabulary")
      cl.append("Degradation")
      cl.append("ProteinReference")
      cl.append("SequenceModificationVocabulary")
      cl.append("Catalysis")
      cl.append("RnaRegionReference")
      cl.append("PhysicalEntity")
      cl.append("Rna")
      cl.append("Evidence")
      cl.append("PathwayStep")
      cl.append("BindingFeature")
      cl.append("DnaRegion")
      cl.append("Stoichiometry")
      cl.append("Pathway")
      cl.append("CellVocabulary")
      cl.append("PublicationXref")
      cl.append("Conversion")
      cl.append("RelationshipXref")
      cl.append("SequenceInterval")
      cl.append("KPrime")
      cl.append("Gene")
      cl.append("ExperimentalForm")
      cl.append("ControlledVocabulary")
      cl.append("ModificationFeature")
      cl.append("GeneticInteraction")
      cl.append("BiochemicalReaction")
      cl.append("DnaReference")
      cl.append("DnaRegionReference")
      cl.append("RnaRegion")
      cl.append("CellularLocationVocabulary")
      cl.append("Modulation")
      cl.append("Xref")
      cl.append("ChemicalStructure")
      cl.append("FragmentFeature")
      cl.append("DeltaG")
      cl.append("UnificationXref")
      cl.append("EvidenceCodeVocabulary")
      cl.append("PhenotypeVocabulary")
      cl.append("EntityFeature")
      cl.append("UtilityClass")
      cl.append("Entity")
  
      return cl


 

def select(cln):
      lcn=cln.lower()
      if lcn is None :
        return None
 
      elif lcn=="templatereaction" :
        return  templatereaction_DocHelper()
 
      elif lcn=="provenance" :
        return  provenance_DocHelper()
 
      elif lcn=="covalentbindingfeature" :
        return  covalentbindingfeature_DocHelper()
 
      elif lcn=="relationshiptypevocabulary" :
        return  relationshiptypevocabulary_DocHelper()
 
      elif lcn=="entityreference" :
        return  entityreference_DocHelper()
 
      elif lcn=="dna" :
        return  dna_DocHelper()
 
      elif lcn=="molecularinteraction" :
        return  molecularinteraction_DocHelper()
 
      elif lcn=="score" :
        return  score_DocHelper()
 
      elif lcn=="rnareference" :
        return  rnareference_DocHelper()
 
      elif lcn=="templatereactionregulation" :
        return  templatereactionregulation_DocHelper()
 
      elif lcn=="complex" :
        return  complex_DocHelper()
 
      elif lcn=="smallmolecule" :
        return  smallmolecule_DocHelper()
 
      elif lcn=="experimentalformvocabulary" :
        return  experimentalformvocabulary_DocHelper()
 
      elif lcn=="sequencelocation" :
        return  sequencelocation_DocHelper()
 
      elif lcn=="smallmoleculereference" :
        return  smallmoleculereference_DocHelper()
 
      elif lcn=="transport" :
        return  transport_DocHelper()
 
      elif lcn=="biosource" :
        return  biosource_DocHelper()
 
      elif lcn=="tissuevocabulary" :
        return  tissuevocabulary_DocHelper()
 
      elif lcn=="complexassembly" :
        return  complexassembly_DocHelper()
 
      elif lcn=="interactionvocabulary" :
        return  interactionvocabulary_DocHelper()
 
      elif lcn=="control" :
        return  control_DocHelper()
 
      elif lcn=="transportwithbiochemicalreaction" :
        return  transportwithbiochemicalreaction_DocHelper()
 
      elif lcn=="sequencesite" :
        return  sequencesite_DocHelper()
 
      elif lcn=="protein" :
        return  protein_DocHelper()
 
      elif lcn=="interaction" :
        return  interaction_DocHelper()
 
      elif lcn=="sequenceregionvocabulary" :
        return  sequenceregionvocabulary_DocHelper()
 
      elif lcn=="biochemicalpathwaystep" :
        return  biochemicalpathwaystep_DocHelper()
 
      elif lcn=="entityreferencetypevocabulary" :
        return  entityreferencetypevocabulary_DocHelper()
 
      elif lcn=="degradation" :
        return  degradation_DocHelper()
 
      elif lcn=="proteinreference" :
        return  proteinreference_DocHelper()
 
      elif lcn=="sequencemodificationvocabulary" :
        return  sequencemodificationvocabulary_DocHelper()
 
      elif lcn=="catalysis" :
        return  catalysis_DocHelper()
 
      elif lcn=="rnaregionreference" :
        return  rnaregionreference_DocHelper()
 
      elif lcn=="physicalentity" :
        return  physicalentity_DocHelper()
 
      elif lcn=="rna" :
        return  rna_DocHelper()
 
      elif lcn=="evidence" :
        return  evidence_DocHelper()
 
      elif lcn=="pathwaystep" :
        return  pathwaystep_DocHelper()
 
      elif lcn=="bindingfeature" :
        return  bindingfeature_DocHelper()
 
      elif lcn=="dnaregion" :
        return  dnaregion_DocHelper()
 
      elif lcn=="stoichiometry" :
        return  stoichiometry_DocHelper()
 
      elif lcn=="pathway" :
        return  pathway_DocHelper()
 
      elif lcn=="cellvocabulary" :
        return  cellvocabulary_DocHelper()
 
      elif lcn=="publicationxref" :
        return  publicationxref_DocHelper()
 
      elif lcn=="conversion" :
        return  conversion_DocHelper()
 
      elif lcn=="relationshipxref" :
        return  relationshipxref_DocHelper()
 
      elif lcn=="sequenceinterval" :
        return  sequenceinterval_DocHelper()
 
      elif lcn=="kprime" :
        return  kprime_DocHelper()
 
      elif lcn=="gene" :
        return  gene_DocHelper()
 
      elif lcn=="experimentalform" :
        return  experimentalform_DocHelper()
 
      elif lcn=="controlledvocabulary" :
        return  controlledvocabulary_DocHelper()
 
      elif lcn=="modificationfeature" :
        return  modificationfeature_DocHelper()
 
      elif lcn=="geneticinteraction" :
        return  geneticinteraction_DocHelper()
 
      elif lcn=="biochemicalreaction" :
        return  biochemicalreaction_DocHelper()
 
      elif lcn=="dnareference" :
        return  dnareference_DocHelper()
 
      elif lcn=="dnaregionreference" :
        return  dnaregionreference_DocHelper()
 
      elif lcn=="rnaregion" :
        return  rnaregion_DocHelper()
 
      elif lcn=="cellularlocationvocabulary" :
        return  cellularlocationvocabulary_DocHelper()
 
      elif lcn=="modulation" :
        return  modulation_DocHelper()
 
      elif lcn=="xref" :
        return  xref_DocHelper()
 
      elif lcn=="chemicalstructure" :
        return  chemicalstructure_DocHelper()
 
      elif lcn=="fragmentfeature" :
        return  fragmentfeature_DocHelper()
 
      elif lcn=="deltag" :
        return  deltag_DocHelper()
 
      elif lcn=="unificationxref" :
        return  unificationxref_DocHelper()
 
      elif lcn=="evidencecodevocabulary" :
        return  evidencecodevocabulary_DocHelper()
 
      elif lcn=="phenotypevocabulary" :
        return  phenotypevocabulary_DocHelper()
 
      elif lcn=="entityfeature" :
        return  entityfeature_DocHelper()
 
      elif lcn=="utilityclass" :
        return  utilityclass_DocHelper()
 
      elif lcn=="entity" :
        return  entity_DocHelper()
 
 
      else:
        return None 



def describe(cln):
   
   prefix=""
   el="\n"
   preferredWidth=70
   wrapper = textwrap.TextWrapper(initial_indent="", width=preferredWidth,
                               subsequent_indent=' '*len(prefix))
   dh=select(cln)
   if dh is None:
     return None

   s="*"*20+el
   s+=str(cln)+el
   s+=dh.classInfo()+el
   s+="-"*20+el
   s+="primitive type attributes:"+el
   for n in  dh.typeAttributeNames():
       s+="-"*10+el
       s+="%s (%s): %s" %(n, dh.attributeType(n),el)
       s+=""+el
       s+=str(wrapper.fill(dh.attributeInfo(n)))
       s+=""+el
   s+="-"*20+el
   s+="object attributes:"+el
   for n in  dh.objectAttributeNames():
       s+="-"*10+el
       s+="%s (%s): %s" %(n, dh.attributeType(n),el)
       s+=""+el
       s+=str(wrapper.fill(dh.attributeInfo(n)))
       s+=""+el
   s+="*"*20+el
   return s

    