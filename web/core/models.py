from neomodel import (
    config,
    StructuredNode,
    StringProperty,
    IntegerProperty,
    RelationshipTo,
    Relationship,
    RelationshipFrom,
    StructuredRel,
    ArrayProperty,
    FloatProperty,
)
from neomodel.contrib import SemiStructuredNode

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'


class EntityRel(StructuredRel):
    confidence = FloatProperty()


class Entity(StructuredNode):
    lemma = StringProperty(unique_index=True, required=True)
    pos = ArrayProperty(StringProperty, required=True)
    shape = StringProperty(required=True)

    synosym = Relationship("Lemma", "SYNONYM", model=EntityRel)
    antonym = Relationship("Lemma", "ANTONYM", model=EntityRel)


class TokenRel(StructuredRel):
    something = StringProperty()


class Token(StructuredNode):
    token = StringProperty(unique_index=True, required=True)

    nsbuj = RelationshipTo('Token', 'NSUBJ', model=TokenRel)
    aux = RelationshipTo('Token', 'AUX', model=TokenRel)
    xcomp = RelationshipTo('Token', 'XCOMP', model=TokenRel)
    acomp = RelationshipTo('Token', 'ACOMP', model=TokenRel)

    lemma = RelationshipTo(Entity, "Lemma")


class TokenToSetRel(StructuredRel):
    """
    order: The order of the token if the group includes multiple. For example if the
           the group token is "Boat" then the order is of the token "Boat" is 0.
           If the group tokens are "The Big Boat" then the order of "The" is 0, the
           order of "Big" is 1 and the order of "Boat" is "2".
    """
    order = IntegerProperty()


class SetRel(StructuredRel):
    confidence = FloatProperty()


class EntitySet(SemiStructuredNode):
    name = StringProperty(unique_index=True, required=True)

    token = RelationshipFrom('Token', 'INCLUDES_TOKEN', model=TokenToSetRel)
    parent = RelationshipTo("Set", "HAS_PARENT`", model=SetRel)
