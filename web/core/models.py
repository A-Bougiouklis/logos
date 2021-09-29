from neomodel import (
    config,
    StructuredNode,
    StringProperty,
    IntegerProperty,
    UniqueIdProperty,
    RelationshipTo,
    RelationshipFrom,
    StructuredRel,
)
from neomodel.contrib import SemiStructuredNode

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'

class TokenRel(StructuredRel):
    something = StringProperty()

class Token(SemiStructuredNode):
    lemma = StringProperty(unique_index=True, required=True)

    nsbuj = RelationshipTo('Token', 'NSUBJ', model=TokenRel)
    aux = RelationshipTo('Token', 'AUX', model=TokenRel)
    xcomp = RelationshipTo('Token', 'XCOMP', model=TokenRel)
    acomp = RelationshipTo('Token', 'ACOMP', model=TokenRel)

class TokenToGroupRel(StructuredRel):
    """
    order: The order of the token if the group includes multiple. For example if the
           the group token is "Boat" then the order is of the token "Boat" is 0.
           If the group tokens are "The Big Boat" then the order of "The" is 0, the
           order of "Big" is 1 and the order of "Boat" is "2".
    """
    order = IntegerProperty()

class GroupToSubgroupRel(StructuredRel):
    something = StringProperty()

class Group(SemiStructuredNode):
    name = StringProperty(unique_index=True, required=True)

    token = RelationshipTo('Token', 'INCLUDES_TOKEN', model=TokenToGroupRel)
    subgroup = RelationshipTo("Group", "HAS_SUBGROUP", model=GroupToSubgroupRel)
