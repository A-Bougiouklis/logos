from django.test import TestCase
from neomodel import clear_neo4j_database

from web.core.models import *
from web.core.analysis import document_analysis

class AtomicityTestClass(TestCase):

    def setUp(self):
        clear_neo4j_database(db)

    def test_create_object(self):
        # with transaction.atomic(using="default"):
        #     with db.transaction:
                # sql_row
                # Tok.objects.create(name="example")
                # neo4j_node
        Token(token="example", shape="foo").save()
        q = Token.nodes.get_or_none(token="example")

        print("HELLO ", q, " !")
        document_analysis("This is a sentence. This is another sentence.")
        #
        # neo4j_q = Book.nodes.get_or_none(title="example")
        # self.assertIsNone(neo4j_q)
        #
        # sql_q = Library.objects.filter(name="example").first()
        # self.assertIsNone(sql_q)