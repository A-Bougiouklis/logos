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
import spacy

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'

nlp = spacy.load("en_core_web_sm")

class EntityRel(StructuredRel):
    confidence = FloatProperty()


class Entity(StructuredNode):
    lemma = StringProperty(unique_index=True, required=True)
    pos = ArrayProperty(StringProperty(), required=True)
    shape = StringProperty(required=True)

    synosym = Relationship("Entity", "SYNONYM", model=EntityRel)
    antonym = Relationship("Entity", "ANTONYM", model=EntityRel)


class TokenRel(StructuredRel):
    dependency = StringProperty()
    sentence_id = IntegerProperty()
    order = IntegerProperty()

class Token(StructuredNode):
    token = StringProperty(unique_index=True, required=True)
    shape = StringProperty()

    dependency = RelationshipTo("Token", "DEPENDENCY", model=TokenRel)
    sentence = RelationshipTo("Token", "SENTENCE", model=TokenRel)

    lemma = RelationshipTo(Entity, "LEMMA")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self):
        doc = nlp(self.token)[0]
        self.shape = doc.shape_
        super().save()
        entity = Entity(lemma=doc.lemma_, pos=[doc.pos_], shape=doc.shape_)
        entity.save()
        self.lemma.connect(entity)
        return self


class TokenToSetRel(StructuredRel):
    """
    order: The order of the token if the group includes multiple. For example if the
           the group token is "Boat" then the order is of the token "Boat" is 0.
           If the group tokens are "The Big Boat" then the order of "The" is 0, the
           order of "Big" is 1 and the order of "Boat" is "2".
    """
    order = IntegerProperty()


class EntitySetRel(StructuredRel):
    confidence = FloatProperty()


class EntitySet(SemiStructuredNode):
    name = StringProperty(unique_index=True, required=True)

    token = RelationshipTo("Token", "NAME", model=TokenToSetRel)
    parent = RelationshipTo("EntitySet", "PARENT", model=EntitySetRel)
