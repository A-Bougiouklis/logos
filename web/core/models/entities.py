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
from nltk.corpus import wordnet


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

    parent = RelationshipTo("Entity", "PARENT", model=EntityRel)
    sentence = RelationshipTo("Entity", "SENTENCE", model=EntityRel)
    synonym = Relationship("Entity", "SYNONYM", model=EntityRel)

    @classproperty
    def nodes(cls):
        return EntityNodeSet(cls)

    @classmethod
    def get_or_create(cls, span: Union[spacy_span, spacy_token]):
        entity_nodes = cls.nodes.filter(text=span.text)

        if not entity_nodes and isinstance(span, spacy_span):
            entity_node = cls(text=span, pos=[span.root.pos_]).save()
            # Create and link the parent of the entity.
            if span.text != span.root.text:
                root_entity_node = cls.get_or_create(span.root).save()
                entity_node.parent.connect(root_entity_node)

        elif not entity_nodes and isinstance(span, spacy_token):
            entity_node = cls(text=span, pos=[span.pos_]).save()

        else:
            entity_node = entity_nodes[0]
            new_pos = span.root.pos_ if isinstance(span, spacy_span) else span.pos_
            if new_pos not in entity_node.pos:
                entity_node.pos.append(new_pos)
                entity_node.save()

        return entity_node

    def generate_synonyms(self, span: Union[spacy_span, spacy_token]):
        """
        - Find all the synonyms for the given entity.
        - Create new entity nodes for each entity that we haven't seen yet.
        - Create a SYNONYM relationship between the given entity and its synonyms.
        """

        if isinstance(span, spacy_span):
            text = "_".join([token.lemma_ for token in span])
        elif isinstance(span, spacy_token):
            text = span.lemma_
        else:
            raise ValueError("Unknown span type.")

        for syn in wordnet.synsets(text):
            for synonym_lemma in syn.lemmas():
                synonym_lemma = synonym_lemma.name().replace("_", " ")
                synonym_nodes = self.nodes.filter(text=synonym_lemma)
                if synonym_nodes and synonym_lemma != span.text:
                    synonym_node = synonym_nodes[0]
                    self.synonym.connect(synonym_node)


class EntitySetRel(StructuredRel):
    confidence = FloatProperty()


class EntitySet(Entity, SemiStructuredNode):

    parent = RelationshipTo("EntitySet", "PARENT", model=EntitySetRel)

    @property
    def not_defined_properties(self) -> dict[str, list[str]]:
        return {
            key: value
            for key, value in self.__dict__.items()
            if key not in ["parent", "sentence", "synonym", "text", "pos", "id"]
        }

    def get_property(self, name: str) -> list[str]:
        name = name.replace(" ", "_")
        try:
            return getattr(self, name)
        except AttributeError:
            return []


    def set_property(self, name: str, value: str):
        name = name.replace(" ", "_")
        changed = False

        if hasattr(self, name):
            properties = set(getattr(self, name))
            if value not in properties:
                properties.add(value)
                setattr(self, name, list(properties))
                changed = True
        else:
            setattr(self, name, [value])
            changed = True

        if changed:
            self.save()
