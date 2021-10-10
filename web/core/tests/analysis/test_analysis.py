# Todo: I need to place some end to end tests.

from django.test import TestCase
from neomodel import clear_neo4j_database
from web.core.models import db, EntitySet, Token
from web.core.analysis.nlp_models import nlp
from web.core.analysis import document_analysis


class EntitySetTests(TestCase):

    # def setUp(self):
    #     clear_neo4j_database(db)


    def test_document_analysis_with_one_big_file(self):
        t = """The masked language model randomly masks some of the tokens from the input, and the objective is to predict the original vocabulary id of the masked"""

        import time
        s = time.time()
        import os, re
        print(os.path.dirname(os.path.abspath(__file__)))
        with open("/opt/project/web/core/tests/analysis/test.txt", "r") as f:
            text = f.read()

        print("Time to read : ", time.time() - s)
        s = time.time()
        sentences = text.split(".")
        cached_nodes = {}
        # Problems with 1682, 3572, 9595, 19220
        # 19221
        # for index, sentence in enumerate(sentences):
        #     try:
        #         sentence = re.sub(r'[^\w\s]', '', sentence)
        #         print(f"{index} out of {len(sentences)}")
        #         cached_nodes = document_analysis(sentence, cached_nodes)
        #     except:
        #         ...
        # print("Needed time to analyse : ", time.time() - s)

        counter = []
        for i in range(20):
            s = time.time()
            # Get every token from a particular sentence
            # results, _ = db.cypher_query(
            #     "MATCH (t:Token)-[:SENTENCE {sentence_id: 4015}]->(:Token) return t"
            # )
            # Get a specific dependency graph
            results, _ = db.cypher_query(
                """MATCH (t0:Token {token:"Philosophy"})-[:DEPENDENCY {dependency: "compound"}]->(t1:Token {token:"Chinese"})-[t2:DEPENDENCY {dependency: "nsubj"}]->(t3:Token {token: "AIControl"}) return t0,t1,t2,t3"""
            )
            counter.append(time.time() - s)

        print("Query time: ", sum(counter)/20)
