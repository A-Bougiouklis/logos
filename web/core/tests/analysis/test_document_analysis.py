from django.test import TestCase
from neomodel import clear_neo4j_database
from neomodel import config
from web.core.models import db, Token
from web.core.analysis import document_analysis
from time import sleep
from subprocess import call
from django.test.runner import DiscoverRunner


class AtomicityTestClass(TestCase):

    def setUp(self) -> None:
        clear_neo4j_database(db)

    def test_create_object(self):
        did = Token(token="did").save()
        when = Token(token="When").save()
        when.sentence.connect(did, {"document_id": 5, "sentence_id": 5, "order": 1})
        Token(token="example", shape="foo").save()
