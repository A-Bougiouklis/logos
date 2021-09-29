from neomodel import (
    config,
    StructuredNode,
    StringProperty,
    IntegerProperty,
    UniqueIdProperty,
    RelationshipTo,
    StructuredRel,
)
from neomodel.contrib import SemiStructuredNode


config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'

class GroupRel(StructuredRel):
    something = StringProperty()

class Token(SemiStructuredNode):
    lemma = StringProperty(unique_index=True, required=True)

    nsbuj = RelationshipTo('Token', 'NSUBJ', model=GroupRel)
    aux = RelationshipTo('Token', 'AUX', model=GroupRel)
    xcomp = RelationshipTo('Token', 'XCOMP', model=GroupRel)
    acomp = RelationshipTo('Token', 'ACOMP', model=GroupRel)
