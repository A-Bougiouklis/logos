from neomodel import (
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
from spacy.tokens.span import Span as spacy_span
from typing import Union


class EntityNodeSet(NodeSet):

    @classmethod
    def __max_sentence_relationship_property(cls, property_name: str) -> int:
        results, _ = db.cypher_query(
            f"MATCH (:Entity)-[r:SENTENCE]-(:Entity) "
            f"return r.{property_name} "
            f"order by r.{property_name} DESC limit 1"
        )
        return results[0][0] if results else 0

    @classproperty
    def max_document_id(cls) -> int:
        return cls.__max_sentence_relationship_property("document_id")

    @classproperty
    def max_sentence_id(cls) -> int:
        return cls.__max_sentence_relationship_property("sentence_id")


class EntityRel(StructuredRel):
    """
    order: The order of the token if the group includes multiple. For example if the
           the group token is "Boat" then the order is of the token "Boat" is 0.
           If the group tokens are "The Big Boat" then the order of "The" is 0, the
           order of "Big" is 1 and the order of "Boat" is "2".
    """

    confidence = FloatProperty()
    document_id = IntegerProperty()
    sentence_id = IntegerProperty()
    order = IntegerProperty()


class Entity(StructuredNode):
    text = StringProperty(unique_index=True, required=True)
    pos = ArrayProperty(StringProperty(), default=[])

    parent = Relationship("Entity", "PARENT", model=EntityRel)
    synonym = Relationship("Entity", "SYNONYM", model=EntityRel)
    sentence = Relationship("Entity", "SENTENCE", model=EntityRel)

    @classproperty
    def nodes(cls):
        return EntityNodeSet(cls)

    @classmethod
    def get_or_create(cls, span: Union[spacy_span, spacy_token]):
        entity_node = cls.nodes.filter(text=span.text)
        if not entity_node and isinstance(span, spacy_span):
            entity_node = cls(text=span, pos=[span.root.pos_]).save()

            # Create and link the parent of the entity.
            if span.text != span.root.text:
                root_entity_node = cls.get_or_create(span.root).save()
                entity_node.parent.connect(root_entity_node)
        elif not entity_node and isinstance(span, spacy_token):
            entity_node = cls(text=span, pos=[span.pos_]).save()
        else:
            entity_node = entity_node[0]
            new_pos = span.root.pos_ if isinstance(span, spacy_span) else span.pos_
            if new_pos not in entity_node.pos:
                entity_node.pos.append(new_pos)
                entity_node.save()

        cls.generate_synonyms(entity_node)
        return entity_node

    @classmethod
    def generate_synonyms(cls, entity_node):
        """
        - Find all the synonyms for the given entity.
        - Create new entity nodes for each entity that we haven't seen yet.
        - Create a SYNONYM relationship between the given entity and its synonyms.
        """
        ...


class EntitySetRel(StructuredRel):
    confidence = FloatProperty()


class EntitySet(Entity, SemiStructuredNode):

    parent = RelationshipTo("EntitySet", "PARENT", model=EntitySetRel)

    def set_property(self, name: str, value: str):
        name = name.replace(" ", "_")

        if hasattr(self, name):
            property = set(getattr(self, name))
            property.add(value)
            setattr(self, name, list(property))
        else:
            setattr(self, name, [value])
