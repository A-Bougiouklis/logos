from neomodel import (
    config,
    StructuredNode,
    StringProperty,
    IntegerProperty,
    RelationshipTo,
    Relationship,
    StructuredRel,
    ArrayProperty,
    FloatProperty,
    NodeSet,
)
from neomodel.util import classproperty
from neomodel.contrib import SemiStructuredNode
from neomodel import db
from spacy.tokens import Token as spacy_token


config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'


class EntityRel(StructuredRel):
    confidence = FloatProperty()


class Entity(StructuredNode):
    lemma = StringProperty(unique_index=True, required=True)
    pos = ArrayProperty(StringProperty(), default=[])
    shape = ArrayProperty(StringProperty(), default=[])

    synosym = Relationship("Entity", "SYNONYM", model=EntityRel)
    antonym = Relationship("Entity", "ANTONYM", model=EntityRel)

    @classmethod
    def get_or_create(cls, doc: spacy_token):
        entity_node = cls.nodes.filter(lemma=doc.lemma_)
        if not entity_node:
            entity_node = cls(lemma=doc.lemma_, shape=[doc.shape_], pos=[doc.pos_]).save()
        else:
            entity_node = entity_node[0]
            changed = False
            if doc.pos_ not in entity_node.pos:
                entity_node.pos.append(doc.pos_)
                changed = True
            if doc.shape_ not in entity_node.shape:
                entity_node.shape.append(doc.shape_)
                changed = True
            if changed:
                entity_node.save()
        return entity_node


class TokenRel(StructuredRel):
    dependency = StringProperty()
    sentence_id = IntegerProperty()
    document_id = IntegerProperty()
    order = IntegerProperty()


class TokenNodeSet(NodeSet):

    @classmethod
    def max_sentence_relationship_property(cls, property_name: str) -> int:
        results, _ = db.cypher_query(
            f"MATCH (t:Token)-[r:SENTENCE]-(t2:Token) "
            f"return r.{property_name} "
            f"order by r.{property_name} DESC limit 1"
        )
        return results[0][0] if results else 0

    @classproperty
    def max_document_id(cls) -> int:
        return cls.max_sentence_relationship_property("document_id")

    @classproperty
    def max_sentence_id(cls) -> int:
        return cls.max_sentence_relationship_property("sentence_id")


class Token(StructuredNode):
    token = StringProperty(unique_index=True, required=True)
    shape = StringProperty()

    dependency = RelationshipTo("Token", "DEPENDENCY", model=TokenRel)
    sentence = RelationshipTo("Token", "SENTENCE", model=TokenRel)

    lemma = RelationshipTo(Entity, "LEMMA")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classproperty
    def nodes(cls):
        return TokenNodeSet(cls)

    @classmethod
    def get_or_create(cls, doc: spacy_token):
        token_node = cls.nodes.filter(token=doc.text)
        if not token_node:
            token_node = cls(token=doc.text, shape=doc.shape_).save()
            entity = Entity.get_or_create(doc)
            token_node.lemma.connect(entity)
        else:
            token_node = token_node[0]
        return token_node


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
