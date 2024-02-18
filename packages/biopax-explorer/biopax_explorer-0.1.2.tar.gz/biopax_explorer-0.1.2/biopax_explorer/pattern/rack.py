import rdfobj as rdfo
from .processing import ProcessingCollection
from biopax import *
from rdfobj.query import EntityNode 
from rdfobj.pattern import Pattern, Step, LocalProcessing
# import required modules
import inspect

class Rack():
    
    """A reference list of Patterns related to BIOPAX use cases."""

    def __init__(self):
       """Initialize the Rack object."""
       self._version_=0.1
       
       # Dictionary containing main patterns

       self.patterns={
           'controlsMetabolicCatalysis': self.controlsMetabolicCatalysis,
           'notBlackboxComplexInComplex': self.notBlackboxComplexInComplex,
           'inComplexWith': self.inComplexWith,
           'inSameComplex': self.inSameComplex,
           'controlsExpressionWithTemplateReac': self.controlsExpressionWithTemplateReac,
           'usedToProduce': self.usedToProduce,
           'reactsWith': self.reactsWith,
           'controlsPhosphorylation': self.controlsPhosphorylation,
           'modifierConv': self.modifierConv,
           'stateChange': self.stateChange,
           'molecularInteraction': self.molecularInteraction,
           'inSameComplexEffectingConversion': self.inSameComplexEffectingConversion,
           'bindsTo': self.bindsTo,
       }

       # Dictionary containing subpatterns

       self.subpatterns={
           'controlsMetabolicCatalysisBothSimple': self.controlsMetabolicCatalysisBothSimple,
           'controlsMetabolicCatalysisControllerComplex': self.controlsMetabolicCatalysisControllerComplex,
           'controlsMetabolicCatalysisControlledComplex': self.controlsMetabolicCatalysisControlledComplex,
           'controlsMetabolicCatalysisBothComplex': self.controlsMetabolicCatalysisBothComplex,
           'stateChangeSimple': self.stateChangeSimple,
           'stateChangeComplex': self.stateChangeComplex,
           'usedToProduceNoComplex': self.usedToProduceNoComplex,
           'usedToProduceLeftComplex': self.usedToProduceLeftComplex,
           'usedToProduceRightComplex': self.usedToProduceRightComplex,
           'usedToProduceBothComplex': self.usedToProduceBothComplex,
           'reactsWithNoComplex': self.reactsWithNoComplex,
           'reactsWithComplex': self.reactsWithComplex,
           'controlsPhosphorylationRightSimple': self.controlsPhosphorylationRightSimple,
           'controlsPhosphorylationControllerComplex': self.controlsPhosphorylationControllerComplex,
           'controlsPhosphorylationLeftComplex': self.controlsPhosphorylationLeftComplex,
           'controlsPhosphorylationRightComplex': self.controlsPhosphorylationRightComplex,
           'controlsPhosphorylationBothComplex': self.controlsPhosphorylationBothComplex,
           'controlsPhosphorylationBothComplexAndComplexController': self.controlsPhosphorylationBothComplexAndComplexController,
           'controlsPhosphorylationControllerAndLeftComplex': self.controlsPhosphorylationControllerAndLeftComplex,
           'controlsPhosphorylationControllerAndRightComplex': self.controlsPhosphorylationControllerAndRightComplex,
           'modifierConvNoComplex': self.modifierConvNoComplex,
           'modifierConvComplex': self.modifierConvComplex,
           'stateChangeNoComplex': self.stateChangeNoComplex,
           'stateChangeComplex': self.stateChangeComplex,
           'controlsStateChangeSimple': self.controlsStateChangeSimple,
           'controlsStateChangeComplexController': self.controlsStateChangeComplexController,
           'controlsStateChangeBothComplex': self.controlsStateChangeBothComplex,
           'controlsStateChangeComplexControllerAndBothComplex': self.controlsStateChangeComplexControllerAndBothComplex,
           'molecularInteractionNoComplex': self.molecularInteractionNoComplex,
           'molecularInteractionComplex': self.molecularInteractionComplex,
           'inSameActiveComplexMolecularInteraction': self.inSameActiveComplexMolecularInteraction,
           'inSameActiveComplexOtherInteraction': self.inSameActiveComplexOtherInteraction,
       }
       
    def inspect(self,fct):
       """Inspect function signature."""
       print(inspect.signature(fct))

    # ------ PATTERNS ------

    def bindsTo(self, entity_node_list: list = None):
        desc="""
        a Complex with a least 2 Components, connects the entities
        """
        if entity_node_list is None:
            entity_node_list = []

        complex = EntityNode("C2", Complex())
        p1 = EntityNode("P1", Protein())
        p2 = EntityNode("P2", Protein())
        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        complex.connectedWith(p1, "component")
        complex.connectedWith(p2, "component")
        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        er1.not_equal(er2)

        entity_node_list.extend([complex, p1, p2, er1, er2])

        p = Pattern()

        step_1 = Step(entity_node_list)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)
        p.description=desc
        return p

    def inSameComplexEffectingConversion(self, entity_node_list: list = None) -> Pattern:
        desc="""
        a Complex  that is the controller of a Conversion with the related Components 
        """
        if entity_node_list is None:
            entity_node_list = []

        conversion = EntityNode("C", Conversion())
        complex = EntityNode("C2", Complex())
        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        complex.connectedWith(pe1, "component")
        complex.connectedWith(pe2, "component")

        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")

        conversion.connectedWith(complex, "controller")

        er1.not_equal(er2)

        entity_node_list.extend([conversion, complex, pe1, pe2, er1, er2])

        p = Pattern()

        step_1 = Step(entity_node_list)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)
        p.description=desc
        return p

    def inSameActiveComplex(self) -> Pattern:
        desc="""
        members of the same active Complex
        """
        p = Pattern()

        entity_node_list_1: list = self.inSameActiveComplexMolecularInteraction()
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.inSameActiveComplexOtherInteraction()
        step_2 = Step(entity_node_list_2)
        step_2.operator = "UNION"
        step_2.do_pk_only = True
        step_2.do_tuple_result = True # Not necessary
        p.processing_step.append(step_2)
        p.description=desc
        return p

    def molecularInteraction(self) -> Pattern:
        desc="""
        a Pattern that define Molecular Interaction participants including Complex
        """
        p = Pattern()

        entity_node_list_1: list = self.molecularInteractionNoComplex()
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.molecularInteractionComplex()
        step_2 = Step(entity_node_list_2)
        step_2.operator = "UNION"
        step_2.do_pk_only = True
        step_2.do_tuple_result = True # Not necessary
        p.processing_step.append(step_2)

        return p

    def controlsStateChange(self) -> Pattern:
        p = Pattern()

        entity_node_list_1: list = self.controlsStateChangeSimple()
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.controlsStateChangeComplexController()
        step_2 = Step(entity_node_list_2)
        step_2.operator = "UNION"
        step_2.do_pk_only = True
        step_2.do_tuple_result = True # Not necessary
        p.processing_step.append(step_2)

        entity_node_list_3: list = self.controlsStateChangeBothComplex()
        step_3 = Step(entity_node_list_3)
        step_3.operator = "UNION"
        step_3.do_pk_only = True
        step_3.do_tuple_result = True # Not necessary
        p.processing_step.append(step_3)

        entity_node_list_4: list = self.controlsStateChangeComplexControllerAndBothComplex()
        step_4 = Step(entity_node_list_4)
        step_4.operator = "UNION"
        step_4.do_pk_only = True
        step_4.do_tuple_result = True # Not necessary
        p.processing_step.append(step_4)

        return p

    def stateChange(self, label: str = None) -> Pattern:
        desc="""Pattern matching State changes for conversions: a Conversion with an input  and an output  (PhysicalEntity)
        that related to the same EntityReference. Complexes are excluded here
        """
        p = Pattern()

        entity_node_list_1: list = self.stateChangeNoComplex(label=label)
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.stateChangeComplex(label=label)
        step_2 = Step(entity_node_list_2)
        step_2.do_pk_only = True
        step_2.do_tuple_result = True # Not necessary
        p.processing_step.append(step_2)
        p.description=desc
        return p

    def modifierConv(self) -> Pattern:
        desc="""
        a Pattern  matching EntityReferences participating to Conversions 
        """
        p = Pattern()

        entity_node_list_1: list = self.modifierConvNoComplex()
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.modifierConvComplex()
        step_2 = Step(entity_node_list_2)
        step_2.do_pk_only = True
        step_2.do_tuple_result = True # Not necessary
        p.processing_step.append(step_2)
        p.description=desc
        return p

    def controlsPhosphorylation(self) -> Pattern:
        desc="""
        a Pattern that define the Control of Phosphorylation, including
        Complex management
        """
        p = Pattern()

        entity_node_list_1: list = self.controlsPhosphorylationRightSimple()
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.controlsPhosphorylationControllerComplex()
        step_2 = Step(entity_node_list_2)
        step_2.do_pk_only = True
        step_2.do_tuple_result = True # Not necessary
        p.processing_step.append(step_2)

        entity_node_list_3: list = self.controlsPhosphorylationLeftComplex()
        step_3 = Step(entity_node_list_3)
        step_3.do_pk_only = True
        step_3.do_tuple_result = True # Not necessary
        p.processing_step.append(step_3)

        entity_node_list_4: list = self.controlsPhosphorylationRightComplex()
        step_4 = Step(entity_node_list_4)
        step_4.do_pk_only = True
        step_4.do_tuple_result = True # Not necessary
        p.processing_step.append(step_4)

        entity_node_list_5: list = self.controlsPhosphorylationBothComplex()
        step_5 = Step(entity_node_list_5)
        step_5.do_pk_only = True
        step_5.do_tuple_result = True # Not necessary
        p.processing_step.append(step_5)

        entity_node_list_6: list = self.controlsPhosphorylationBothComplexAndComplexController()
        step_6 = Step(entity_node_list_6)
        step_6.do_pk_only = True
        step_6.do_tuple_result = True # Not necessary
        p.processing_step.append(step_6)

        entity_node_list_7: list = self.controlsPhosphorylationControllerAndLeftComplex()
        step_7 = Step(entity_node_list_7)
        step_7.do_pk_only = True
        step_7.do_tuple_result = True # Not necessary
        p.processing_step.append(step_7)

        entity_node_list_8: list = self.controlsPhosphorylationControllerAndRightComplex()
        step_8 = Step(entity_node_list_8)
        step_8.do_pk_only = True
        step_8.do_tuple_result = True # Not necessary
        p.processing_step.append(step_8)
        p.description=desc
        return p

    def reactsWith(self) -> Pattern:
        desc="""
        Constructs a pattern where first and last small molecules are substrates to the same
        biochemical reaction.
        """
        p = Pattern()

        entity_node_list_1: list = self.reactsWithNoComplex()
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        step_1.add_children = False
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.reactsWithComplex()
        step_2 = Step(entity_node_list_2)
        step_2.operator="UNION"
        step_2.do_pk_only = True
        step_2.do_tuple_result = True # Not necessary
        step_2.add_children = False
        p.processing_step.append(step_2)
        p.description=desc
        return p

    def usedToProduce(self) -> Pattern:
        desc="""
          A Pattern that associate 2 small molecules, product and substrat of a
	      biochemical reaction.
        """
        p = Pattern()

        entity_node_list_1: list = self.usedToProduceNoComplex()
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.usedToProduceLeftComplex()
        step_2 = Step(entity_node_list_2)
        step_2.operator="UNION"
        step_2.do_pk_only = True
        step_2.do_tuple_result = True
        p.processing_step.append(step_2)

        # Complex only at left

        # entity_node_list_3: list = self.usedToProduceRightComplex()
        # step_3 = Step(entity_node_list_3)
        # step_3.operator="UNION"
        # step_3.do_pk_only = True
        # step_3.do_tuple_result = True
        # p.processing_step.append(step_3)

        # entity_node_list_4: list = self.usedToProduceBothComplex()
        # step_4 = Step(entity_node_list_4)
        # step_4.operator="UNION"
        # step_4.do_pk_only = True
        # step_4.do_tuple_result = True
        # p.processing_step.append(step_4)
        
        lp_step_5 = LocalProcessing()
        step_5 = Step(lp_step_5)
        pc = ProcessingCollection()
        lp_step_5.method = pc.localProcessingCollection['usedToProduceProcessing']
        step_5.do_pk_only = True
        step_5.do_tuple_result = True
        p.processing_step.append(step_5)
        p.description=desc
        return p

    def controlsMetabolicCatalysis(self) -> Pattern:
        desc="""
        Pattern for a Protein controlling a reaction whose participant is a small molecule.
        The controller is in a Complex 
        """

        p = Pattern()
        
        entity_node_list_1: list = self.controlsMetabolicCatalysisBothSimple()
        step_1 = Step(entity_node_list_1)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)

        entity_node_list_2: list = self.controlsMetabolicCatalysisControllerComplex()
        step_2 = Step(entity_node_list_2)
        step_2.operator = "UNION"
        step_2.do_pk_only = True
        step_2.do_tuple_result = True # Not necessary
        p.processing_step.append(step_2)

        entity_node_list_3: list = self.controlsMetabolicCatalysisControlledComplex()
        step_3 = Step(entity_node_list_3)
        step_3.operator = "UNION"
        step_3.do_pk_only = True
        step_3.do_tuple_result = True # Not necessary
        p.processing_step.append(step_3)

        entity_node_list_4: list = self.controlsMetabolicCatalysisBothComplex()
        step_4 = Step(entity_node_list_4)
        step_4.operator = "UNION"
        step_4.do_pk_only = True
        step_4.do_tuple_result = True # Not necessary
        p.processing_step.append(step_4)
        p.description=desc
        return p


    def notBlackboxComplexInComplex(self, entity_node_list:list = None):
        desc="""
        Pattern to detect inconsistant complex (recursive complexes of complexes)
        """
        if entity_node_list is None:
            entity_node_list = []

        c_initial = EntityNode("C1", Complex())
        c_2 = EntityNode("C2", Complex())
        pe = EntityNode("PE", PhysicalEntity())

        c_initial.connectedWith(c_2, "component")
        c_2.connectedWith(pe, "component")

        entity_node_list.extend([c_initial, c_2, pe])

        p = Pattern()
        step_1 = Step(entity_node_list)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)
        p.description=desc 
        return p
    
    def inComplexWith(self, entity_node_list: list = None):
        desc="""
        A Pattern that defines two proteins have states that are members of the same complex. Handles nested complexes and
        homologies. Also guarantees that relationship to the complex is through different direct
        complex members.
        """
        if entity_node_list is None:
            entity_node_list = []

        complex = EntityNode("COMPLEX", Complex())

        p1 = EntityNode("P1", [Protein()])
        p2 = EntityNode("P2", [Protein()])

        pr1 = EntityNode("PR1", ProteinReference())
        pr2 = EntityNode("PR2", ProteinReference())

        complex.connectedWith(p1, "component")
        complex.connectedWith(p2, "component")

        p1.connectedWith(pr2, "entityReference")
        p2.connectedWith(pr1, "entityReference")

        p1.not_equal(p2)

        pr1.not_equal(pr2)

        entity_node_list.extend([complex, p1, p2, pr1, pr2])

        p = Pattern()
        step_1 = Step(entity_node_list)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)
        p.description=desc
        return p
    
    def controlsExpressionWithConversion(self, entity_node_list: list = None):
        desc="""
        a Pattern defining the Control of a Conversion
          and the related products
        """
        if entity_node_list is None:
            entity_node_list = []

        control = EntityNode("Control", Control())

        conversion = EntityNode("TR", Conversion())

        pe1 = EntityNode("Controller", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), Complex()])

        pe2 = EntityNode("Product", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion()])

        control.connectedWith(conversion, "controlled")

        control.connectedWith(pe1, "controller")

        conversion.connectedWith(pe2, "product")

        entity_node_list.extend([control, conversion, pe1, pe2])

        p = Pattern()
        step_1 = Step(entity_node_list)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)
        p.description=desc
        return p
    
    def controlsExpressionWithTemplateReac(self, entity_node_list: list = None):
        desc="""
        a Pattern defining the control of  a TemplateReation and the related products
        """
        if entity_node_list is None:
            entity_node_list = []

        control = EntityNode("Control", Control())

        tr = EntityNode("TR", TemplateReaction())

        pe1 = EntityNode("Controller", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), Complex()])

        pe2 = EntityNode("Product", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion()])

        control.connectedWith(tr, "controlled")

        control.connectedWith(pe1, "controller")

        tr.connectedWith(pe2, "product")

        entity_node_list.extend([control, tr, pe1, pe2])

        p = Pattern()
        step_1 = Step(entity_node_list)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)
        p.description=desc
        return p
    
    def inSameComplex(self, entity_node_list: list = None):
        desc="""
        Pattern for two different EntityReference have member PhysicalEntity in the same Complex.
        Complex membership can be through multiple nesting and/or through homology relations.
        """
        if entity_node_list is None:
            entity_node_list = []

        complex = EntityNode("COMPLEX", Complex())

        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        complex.connectedWith(pe1, "component")
        complex.connectedWith(pe2, "component")
        pe1.not_equal(pe2)
        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")
        er1.not_equal(er2)

        entity_node_list.extend([complex, pe1, pe2, er1, er2])
        
        p = Pattern()
        step_1 = Step(entity_node_list)
        step_1.do_pk_only = True
        step_1.do_tuple_result = True # Not necessary
        p.processing_step.append(step_1)
        p.description=desc
        return p

    # ------ SUBPATTERNS ------

    # inSameActiveComplex SubPatterns

    def inSameActiveComplexMolecularInteraction(self, entity_node_list: list = None):
        """
        
        """
        if entity_node_list is None:
            entity_node_list = []
        mi = EntityNode("MI", MolecularInteraction())
        c1 = EntityNode("C1", Complex())
        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        c1.connectedWith(pe1, "component")
        c1.connectedWith(pe2, "component")

        mi.connectedWith(c1, "participant")

        pe1.not_equal(pe2)

        entity_node_list.extend([mi, c1, pe1, pe2])

        return entity_node_list
    
    def inSameActiveComplexOtherInteraction(self, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []
        mi = EntityNode("MI", Interaction())
        c1 = EntityNode("C1", Complex())
        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        c1.connectedWith(pe1, "component")
        c1.connectedWith(pe2, "component")

        mi.connectedWith(c1, "controller")

        pe1.not_equal(pe2)

        entity_node_list.extend([mi, c1, pe1, pe2])
        
        return entity_node_list

    # molecularInteraction SubPatterns

    def molecularInteractionNoComplex(self, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []
        mi = EntityNode("MI", MolecularInteraction())
        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        mi.connectedWith(pe1, "participant")
        mi.connectedWith(pe2, "participant")

        pe1.not_equal(pe2)

        entity_node_list.extend([mi, pe1, pe2])

        return entity_node_list

    def molecularInteractionComplex(self, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []
        mi = EntityNode("MI", MolecularInteraction())
        c1 = EntityNode("C1", Complex())
        c2 = EntityNode("C2", Complex())
        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        c1.connectedWith(pe1, "component")
        c2.connectedWith(pe2, "component")

        mi.connectedWith(c1, "participant")
        mi.connectedWith(c2, "participant")

        pe1.not_equal(pe2)

        entity_node_list.extend([mi, c1, c2, pe1, pe2])

        return entity_node_list

    # controlsStateChange SubPatterns

    def controlsStateChangeSimple(self, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Conversion())

        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe3 = EntityNode("PE3", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())
        er3 = EntityNode("ER3", EntityReference())

        control.connectedWith(interaction, "controlled")
        control.connectedWith(pe3, 'controller')

        interaction.connectedWith(pe1, "left")
        interaction.connectedWith(pe2, "right")

        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")

        er1.equal(er2)

        pe3.connectedWith(er3, "entityReference")
        er1.not_equal(er3)

        entity_node_list.extend([control, interaction, pe1, pe2, pe3, er1, er2, er3])

        return entity_node_list

    def controlsStateChangeComplexController(self, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        complex3 = EntityNode("Complex", Complex())

        pe3 = EntityNode("PE3", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())
        er3 = EntityNode("ER3", EntityReference())

        complex3.connectedWith(pe3, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(complex3, 'controller')

        interaction.connectedWith(pe1, "left")
        interaction.connectedWith(pe2, "right")

        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")

        er1.equal(er2)

        pe3.connectedWith(er3, "entityReference")
        er1.not_equal(er3)

        entity_node_list.extend([control, interaction, complex3, pe1, pe2, pe3, er1, er2, er3])

        return entity_node_list

    def controlsStateChangeComplexControllerAndBothComplex(self, entity_node_list : list = None):
        if entity_node_list is None:
            entity_node_list = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        complex1 = EntityNode("Complex1", Complex())
        complex2 = EntityNode("Complex2", Complex())
        complex3 = EntityNode("Complex3", Complex())

        pe3 = EntityNode("PE3", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())
        er3 = EntityNode("ER3", EntityReference())

        complex1.connectedWith(pe1, "component")
        complex2.connectedWith(pe2, "component")
        complex3.connectedWith(pe3, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(complex3, 'controller')

        interaction.connectedWith(complex1, "left")
        interaction.connectedWith(complex2, "right")

        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")

        er1.equal(er2)

        pe3.connectedWith(er3, "entityReference")
        er1.not_equal(er3)

        entity_node_list.extend([control, interaction, complex1, complex2, complex3, pe1, pe2, pe3, er1, er2, er3])

        return entity_node_list
    
    def controlsStateChangeBothComplex(self, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        pe1 = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        pe2 = EntityNode("PE2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        complex1 = EntityNode("Complex1", Complex())
        complex2 = EntityNode("Complex2", Complex())

        pe3 = EntityNode("PE3", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())
        er3 = EntityNode("ER3", EntityReference())

        complex1.connectedWith(pe1, "component")
        complex2.connectedWith(pe2, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(pe3, 'controller')

        interaction.connectedWith(complex1, "left")
        interaction.connectedWith(complex2, "right")

        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")

        er1.equal(er2)

        pe3.connectedWith(er3, "entityReference")
        er1.not_equal(er3)

        entity_node_list.extend([control, interaction, complex1, complex2, pe1, pe2, pe3, er1, er2, er3])
        
        return entity_node_list

    # stateChange SubPatterns

    def stateChangeNoComplex(self, label: str = None, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []

        conversion = EntityNode("c", Conversion())

        pe1 = EntityNode("pe1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        pe2 = EntityNode("pe2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        conversion.connectedWith(pe1, "left")
        conversion.connectedWith(pe2, "right")

        if label is not None:
            pe1.whereAttribute("name", label, "EQ")

        er1 = EntityNode("er1", EntityReference())
        er2 = EntityNode("er2", EntityReference())

        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")

        er1.equal(er2)
        entity_node_list.extend([conversion, pe1, pe2, er1, er2])

        return entity_node_list

    def stateChangeComplex(self, label: str = None, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []

        conversion = EntityNode("c", Conversion())

        complex1 = EntityNode("Complex1", Complex())
        complex2 = EntityNode("Complex2", Complex())

        pe1 = EntityNode("pe1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        pe2 = EntityNode("pe2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        complex1.connectedWith(pe1, "component")
        complex2.connectedWith(pe2, "component")
        conversion.connectedWith(complex1, "left")
        conversion.connectedWith(complex2, "right")

        if label is not None:
            pe1.whereAttribute("name", label, "EQ")

        er1 = EntityNode("er1", EntityReference())
        er2 = EntityNode("er2", EntityReference())

        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")

        er1.equal(er2)

        entity_node_list.extend([conversion, complex1, complex2, pe1, pe2, er1, er2])
        
        return entity_node_list

    # ModifierConv SubPatterns

    def modifierConvNoComplex(self, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []
        conv = EntityNode("C1", Conversion())
        pe = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        y2 = EntityNode("ER", EntityReference())

        pe.connectedWith(y2, "entityReference")
        conv.connectedWith(pe, ["left", "right"])

        entity_node_list.extend([conv, pe, y2])

        return entity_node_list

    def modifierConvComplex(self, entity_node_list: list = None):
        if entity_node_list is None:
            entity_node_list = []
        conv = EntityNode("C1", Conversion())
        complex1 = EntityNode("Complex", Complex())
        pe = EntityNode("PE1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        y2 = EntityNode("ER", EntityReference())

        complex1.connectedWith(pe, "component")
        pe.connectedWith(y2, "entityReference")
        conv.connectedWith(complex1, ["left", "right"])

        entity_node_list.extend([conv, complex1, pe, y2])

        return entity_node_list

    # controlsPhosphorylation SubPatterns :

    def controlsPhosphorylationRightSimple(self, enl: list = None):
        if enl is None:
            enl = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        controller = EntityNode("Controller", Protein())

        p1 = EntityNode("P1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        p2 = EntityNode("P2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        modif = EntityNode("MF1", ModificationFeature())

        smv = EntityNode("SMV1", SequenceModificationVocabulary())

        control.connectedWith(interaction, "controlled")
        control.connectedWith(controller, "controller")

        interaction.connectedWith(p1,"left")
        interaction.connectedWith(p2,"right")

        p2.connectedWith(modif, "feature")

        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        modif.connectedWith(smv, "modificationType")

        p1.not_equal(p2)
        er1.equal(er2)

        smv.whereAttribute("term", "phospho", 'CONTAINS')

        enl.extend([control, interaction, controller, p1, p2, er1, er2, modif, smv])

        return enl
    
    def controlsPhosphorylationControllerComplex(self, enl: list = None):
        if enl is None:
            enl = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        complex = EntityNode("Complex", Complex())

        controller = EntityNode("Controller", Protein())

        p1 = EntityNode("P1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        p2 = EntityNode("P2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        modif = EntityNode("MF1", ModificationFeature())

        smv = EntityNode("SMV1", SequenceModificationVocabulary())

        complex.connectedWith(controller, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(complex, "controller")

        interaction.connectedWith(p1,"left")
        interaction.connectedWith(p2,"right")

        p2.connectedWith(modif, "feature")

        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        modif.connectedWith(smv, "modificationType")

        p1.not_equal(p2)
        er1.equal(er2)

        smv.whereAttribute("term", "phospho", 'CONTAINS')

        enl.extend([control, interaction, complex, controller, p1, p2, er1, er2, modif, smv])

        return enl
    

    
    def controlsPhosphorylationLeftComplex(self, enl: list = None):
        if enl is None:
            enl = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        complex = EntityNode("Complex", Complex())

        controller = EntityNode("Controller", Protein())

        p1 = EntityNode("P1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        p2 = EntityNode("P2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        modif = EntityNode("MF1", ModificationFeature())

        smv = EntityNode("SMV1", SequenceModificationVocabulary())

        complex.connectedWith(p1, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(controller, "controller")

        interaction.connectedWith(complex,"left")
        interaction.connectedWith(p2,"right")

        p2.connectedWith(modif, "feature")

        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        modif.connectedWith(smv, "modificationType")

        p1.not_equal(p2)
        er1.equal(er2)

        smv.whereAttribute("term", "phospho", 'CONTAINS')

        enl.extend([control, interaction, complex, controller, p1, p2, er1, er2, modif, smv])

        return enl
    

    
    def controlsPhosphorylationRightComplex(self, enl: list = None):
        if enl is None:
            enl = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        complex = EntityNode("Complex", Complex())

        controller = EntityNode("Controller", Protein())

        p1 = EntityNode("P1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        p2 = EntityNode("P2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        modif = EntityNode("MF1", ModificationFeature())

        smv = EntityNode("SMV1", SequenceModificationVocabulary())

        complex.connectedWith(p2, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(controller, "controller")

        interaction.connectedWith(p1,"left")
        interaction.connectedWith(complex,"right")

        p2.connectedWith(modif, "feature")

        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        modif.connectedWith(smv, "modificationType")

        p1.not_equal(p2)
        er1.equal(er2)

        smv.whereAttribute("term", "phospho", 'CONTAINS')

        enl.extend([control, interaction, complex, controller, p1, p2, er1, er2, modif, smv])

        return enl


    
    def controlsPhosphorylationBothComplex(self, enl: list = None):
        if enl is None:
            enl = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        complex1 = EntityNode("Complex1", Complex())
        complex2 = EntityNode("Complex2", Complex())

        controller = EntityNode("Controller", Protein())

        p1 = EntityNode("P1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        p2 = EntityNode("P2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        modif = EntityNode("MF1", ModificationFeature())

        smv = EntityNode("SMV1", SequenceModificationVocabulary())

        complex1.connectedWith(p1, "component")
        complex2.connectedWith(p2, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(controller, "controller")

        interaction.connectedWith(complex1,"left")
        interaction.connectedWith(complex2,"right")

        p2.connectedWith(modif, "feature")

        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        modif.connectedWith(smv, "modificationType")

        p1.not_equal(p2)
        er1.equal(er2)

        smv.whereAttribute("term", "phospho", 'CONTAINS')

        enl.extend([control, interaction, complex1, complex2, controller, p1, p2, er1, er2, modif, smv])
        
        return enl
    
    def controlsPhosphorylationBothComplexAndComplexController(self, enl: list = None):
        if enl is None:
            enl = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        complex1 = EntityNode("Complex1", Complex())
        complex2 = EntityNode("Complex2", Complex())
        complex3 = EntityNode("Complex3", Complex())

        controller = EntityNode("Controller", Protein())

        p1 = EntityNode("P1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        p2 = EntityNode("P2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        modif = EntityNode("MF1", ModificationFeature())

        smv = EntityNode("SMV1", SequenceModificationVocabulary())

        complex1.connectedWith(p1, "component")
        complex2.connectedWith(p2, "component")
        complex2.connectedWith(controller, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(complex3, "controller")

        interaction.connectedWith(complex1,"left")
        interaction.connectedWith(complex2,"right")

        p2.connectedWith(modif, "feature")

        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        modif.connectedWith(smv, "modificationType")

        p1.not_equal(p2)
        er1.equal(er2)

        smv.whereAttribute("term", "phospho", 'CONTAINS')

        enl.extend([control, interaction, complex1, complex2, complex3, controller, p1, p2, er1, er2, modif, smv])

        return enl

    def controlsPhosphorylationControllerAndLeftComplex(self, enl: list = None):
        if enl is None:
            enl = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        complex1 = EntityNode("Complex1", Complex())
        complex2 = EntityNode("Complex2", Complex())

        controller = EntityNode("Controller", Protein())

        p1 = EntityNode("P1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        p2 = EntityNode("P2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        modif = EntityNode("MF1", ModificationFeature())

        smv = EntityNode("SMV1", SequenceModificationVocabulary())

        complex1.connectedWith(p1, "component")
        complex2.connectedWith(controller, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(complex2, "controller")

        interaction.connectedWith(complex1,"left")
        interaction.connectedWith(p2,"right")

        p2.connectedWith(modif, "feature")

        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        modif.connectedWith(smv, "modificationType")

        p1.not_equal(p2)
        er1.equal(er2)

        smv.whereAttribute("term", "phospho", 'CONTAINS')

        enl.extend([control, interaction, complex1, complex2, controller, p1, p2, er1, er2, modif, smv])

        return enl
    
    def controlsPhosphorylationControllerAndRightComplex(self, enl: list = None):
        if enl is None:
            enl = []

        control = EntityNode("C1", Control())

        interaction = EntityNode("I", Interaction())

        complex1 = EntityNode("Complex1", Complex())
        complex2 = EntityNode("Complex2", Complex())

        controller = EntityNode("Controller", Protein())

        p1 = EntityNode("P1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        p2 = EntityNode("P2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        modif = EntityNode("MF1", ModificationFeature())

        smv = EntityNode("SMV1", SequenceModificationVocabulary())

        complex1.connectedWith(controller, "component")
        complex2.connectedWith(p2, "component")

        control.connectedWith(interaction, "controlled")
        control.connectedWith(complex1, "controller")

        interaction.connectedWith(p1,"left")
        interaction.connectedWith(complex2,"right")

        p2.connectedWith(modif, "feature")

        p1.connectedWith(er1, "entityReference")
        p2.connectedWith(er2, "entityReference")

        modif.connectedWith(smv, "modificationType")

        p1.not_equal(p2)
        er1.equal(er2)

        smv.whereAttribute("term", "phospho", 'CONTAINS')

        enl.extend([control, interaction, complex1, complex2, controller, p1, p2, er1, er2, modif, smv])

        return enl

    def reactsWithNoComplex(self, enl: list = None):
        if enl is None:
            enl = []

        br1 = EntityNode("BR1", BiochemicalReaction())

        sm1 = EntityNode("SM1", SmallMolecule())
        sm2 = EntityNode("SM2", SmallMolecule())

        smr1 = EntityNode("SMR1", SmallMoleculeReference())
        smr2 = EntityNode("SMR2", SmallMoleculeReference())


        br1.connectedWith(sm1, "left")
        br1.connectedWith(sm2, "left")

        sm1.not_equal(sm2)

        sm1.connectedWith(smr1, "entityReference")
        sm2.connectedWith(smr2, "entityReference")

        enl.extend([br1, sm1, sm2, smr1, smr2])

        return enl
    
    def reactsWithComplex(self, enl: list = None):
        if enl is None:
            enl = []

        br1 = EntityNode("BR1", BiochemicalReaction())

        complex = EntityNode("C", Complex())

        sm1 = EntityNode("SM1", SmallMolecule())
        sm2 = EntityNode("SM2", SmallMolecule())

        smr1 = EntityNode("SMR1", SmallMoleculeReference())
        smr2 = EntityNode("SMR2", SmallMoleculeReference())

        br1.connectedWith(complex, "left")
        br1.connectedWith(sm2, "left")

        complex.connectedWith(sm1, "component")

        sm1.not_equal(sm2)

        sm1.connectedWith(smr1, "entityReference")
        sm2.connectedWith(smr2, "entityReference")


        enl.extend([br1, complex, sm1, sm2, smr1, smr2])

        return enl

    def usedToProduceNoComplex(self, enl: list = None):
        """
        Constructs a pattern where first small molecule is an input a biochemical reaction that
        produces the second small molecule.
        """
        if enl is None:
            enl = []

        br = EntityNode("BR", BiochemicalReaction())

        sm1 = EntityNode("SM1", SmallMolecule())
        sm2 = EntityNode("SM2", SmallMolecule())


        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        sm1.connectedWith(er1, "entityReference")
        sm2.connectedWith(er2, "entityReference")

        br.connectedWith(sm1, "left")
        br.connectedWith(sm2, "right")

        # sm1.not_equal(sm2)

        # er1.not_equal(er2)

        enl.extend([br, sm1, sm2, er1, er2])
        
        return enl
    
    def usedToProduceLeftComplex(self, enl: list = None):
        """
        Constructs a pattern where first small molecule is an input a biochemical reaction that
        produces the second small molecule.
        Complex at left
        """
        if enl is None:
            enl = []

        br = EntityNode("BR", BiochemicalReaction())

        c = EntityNode("C", Complex())

        sm1 = EntityNode("SM1", SmallMolecule())
        sm2 = EntityNode("SM2", SmallMolecule())


        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        sm1.connectedWith(er1, "entityReference")
        sm2.connectedWith(er2, "entityReference")

        c.connectedWith(sm1, "component")

        br.connectedWith(c, "left")
        br.connectedWith(sm2, "right")

        # sm1.not_equal(sm2)

        # er1.not_equal(er2)

        enl.extend([br, c, sm1, sm2, er1, er2])

        return enl

    def usedToProduceRightComplex(self, enl: list = None):
        """
        Constructs a pattern where first small molecule is an input a biochemical reaction that
        produces the second small molecule.
        Complex at right
        """
        if enl is None:
            enl = []

        br = EntityNode("BR", BiochemicalReaction())

        c = EntityNode("C", Complex())

        sm1 = EntityNode("SM1", SmallMolecule())
        sm2 = EntityNode("SM2", SmallMolecule())


        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        sm1.connectedWith(er1, "entityReference")
        sm2.connectedWith(er2, "entityReference")

        c.connectedWith(sm2, "component")

        br.connectedWith(sm1, "left")
        br.connectedWith(c, "right")

        # sm1.not_equal(sm2)

        # er1.not_equal(er2)

        enl.extend([br, c, sm1, sm2, er1, er2])

        return enl

    def usedToProduceBothComplex(self, enl: list = None):
        """
        Constructs a pattern where first small molecule is an input a biochemical reaction that
        produces the second small molecule.
        Complex at left and at right
        """
        if enl is None:
            enl = []

        br = EntityNode("BR", BiochemicalReaction())

        c1 = EntityNode("C1", Complex())
        c2 = EntityNode("C2", Complex())

        sm1 = EntityNode("SM1", SmallMolecule())
        sm2 = EntityNode("SM2", SmallMolecule())


        er1 = EntityNode("ER1", EntityReference())
        er2 = EntityNode("ER2", EntityReference())

        sm1.connectedWith(er1, "entityReference")
        sm2.connectedWith(er2, "entityReference")

        c1.connectedWith(sm1, "component")
        c2.connectedWith(sm2, "component")

        br.connectedWith(c1, "left")
        br.connectedWith(c2, "right")

        # sm1.not_equal(sm2)

        # er1.not_equal(er2)

        enl.extend([br, c1, c2, sm1, sm2, er1, er2])

        return enl

    def controlsMetabolicCatalysisBothSimple(self, enl:list = None):
        """
        Pattern for a Protein controlling a reaction whose participant is a small molecule.
        The controller and the participant is not a Complex 
        """
        if enl is None:
            enl = []

        control = EntityNode("Control", Control())

        interaction = EntityNode("I", Interaction())

        protein = EntityNode("Controller", Protein())

        sm = EntityNode("SM", SmallMolecule())

        control.connectedWith(interaction, "controlled")
        control.connectedWith(protein, "controller")
        interaction.connectedWith(sm, ["left", "right"])

        enl.extend([control, interaction, protein, sm])

        return enl
    
    def controlsMetabolicCatalysisControllerComplex(self, enl: list = None):
        """
        Pattern for a Protein controlling a reaction whose participant is a small molecule.
        The controller is in a Complex 
        """
        if enl is None:
            enl = []

        control = EntityNode("Control", Control())

        interaction = EntityNode("I", Interaction())

        complex_controller = EntityNode("complex", Complex())

        protein = EntityNode("Controller", Protein())

        sm = EntityNode("SM", SmallMolecule())

        control.connectedWith(interaction, "controlled")
        control.connectedWith(complex_controller, "controller")
        complex_controller.connectedWith(protein, "component")
        interaction.connectedWith(sm, ["left", "right"])

        enl.extend([control, complex_controller, interaction, protein, sm])

        return enl
    
    def controlsMetabolicCatalysisControlledComplex(self, enl: list = None):
        """
        Pattern for a Protein controlling a reaction whose participant is a small molecule.
        The participant is in a Complex 
        """
        if enl is None:
            enl = []

        control = EntityNode("Control", Control())

        interaction = EntityNode("I", Interaction())

        protein = EntityNode("Controller", Protein())

        complex_controlled = EntityNode("Comp_cont", Complex())

        sm = EntityNode("SM", SmallMolecule())

        control.connectedWith(interaction, "controlled")
        control.connectedWith(protein, "controller")
        interaction.connectedWith(complex_controlled, ["left", "right"])
        complex_controlled.connectedWith(sm, "component")

        enl.extend([control, interaction, complex_controlled, protein, sm])

        return enl

    def controlsMetabolicCatalysisBothComplex(self, enl: list = None):
        """
        Pattern for a Protein controlling a reaction whose participant is a small molecule.
        The controller and the participant are both in a Complex 
        """
        if enl is None:
            enl = []

        control = EntityNode("Control", Control())

        interaction = EntityNode("I", Interaction())

        complex_controller = EntityNode("complex", Complex())

        protein = EntityNode("Controller", Protein())

        complex_controlled = EntityNode("Comp_cont", Complex())

        sm = EntityNode("SM", SmallMolecule())

        
        control.connectedWith(complex_controller, "controller")
        control.connectedWith(interaction, "controlled")

        interaction.connectedWith(complex_controlled, ["left", "right"])

        complex_controller.connectedWith(protein, "component")
        
        complex_controlled.connectedWith(sm, "component")

        enl.extend([control, interaction, complex_controller, complex_controlled, protein, sm])

        return enl

    def stateChangeSimple(self, label = None, enl:list = None):
        """
        Pattern for a Conversion has an input PhysicalEntity (except Complex) and another output PhysicalEntity (except Complex) 
        that belongs to the same EntityReference
        
        Args:
            label (str): input name
        """
        if enl is None:
            enl = []

        conversion = EntityNode("c", Conversion())

        pe1 = EntityNode("pe1", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])

        pe2 = EntityNode("pe2", [Protein(), Rna(), RnaRegion(), Dna(), DnaRegion(), SmallMolecule()])
        conversion.connectedWith(pe1, "left")
        conversion.connectedWith(pe2, "right")

        if label is not None:
            pe1.whereAttribute("name", label, "EQ")

        er1 = EntityNode("er1", EntityReference())
        er2 = EntityNode("er2", EntityReference())

        pe1.connectedWith(er1, "entityReference")
        pe2.connectedWith(er2, "entityReference")

        pe1.not_equal(pe2)

        er1.equal(er2)

        enl.extend([conversion, pe1, pe2, er1, er2])

        return enl

    def stateChangeComplex(self,label = None,enl:list = None):
        if enl is None:
            enl = []

        conv = EntityNode("Conv", Conversion())

        c1 = EntityNode("c1", Complex())

        if label is not None:
            c1.whereAttribute("name", label, "EQ")

        c2 = EntityNode("c2", Complex())

        conv.connectedWith(c1, "left")
        conv.connectedWith(c2, "right")

        enl.extend([conv, c1, c2])

        return enl
    
    # ------------------------------