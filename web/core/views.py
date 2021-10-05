from django.http import HttpResponse
from .models import *

def home(request):
    return create_coded_nodes()

def create_coded_nodes():

    delete_old_nodes()

    when = Token(token="When").save()
    andreas = Token(token="Andreas").save()
    bougiouklis = Token(token="Bougiouklis").save()
    start = Token(token="start").save()
    did = Token(token="did").save()
    becoming = Token(token="becoming").save()
    tall = Token(token="tall").save()

    when.sentence.connect(did, {"document_id": 0, "sentence_id": 0, "order": 1})
    did.sentence.connect(andreas, {"document_id": 0, "sentence_id": 0, "order": 2})
    andreas.sentence.connect(bougiouklis, {"document_id": 0, "sentence_id": 0, "order": 3})
    bougiouklis.sentence.connect(start, {"document_id": 0, "sentence_id": 0, "order": 4})
    start.sentence.connect(becoming, {"document_id": 0, "sentence_id": 0, "order": 5})
    becoming.sentence.connect(tall, {"document_id": 0, "sentence_id": 0, "order": 6})

    when.dependency.connect(did, {"dependency": "acomp"})
    start.dependency.connect(andreas, {"dependency": "nsbuj"})
    start.dependency.connect(did, {"dependency": "aux"})
    start.dependency.connect(becoming, {"dependency": "xcomp"})
    becoming.dependency.connect(tall, {"dependency": "acomp"})
    andreas.dependency.connect(bougiouklis, {"dependency": "acomp"})

    andreas_group = EntitySet(name="Andreas").save()
    andreas_bougiouklis_group = EntitySet(name="Andreas Bougiouklis").save()

    andreas_bougiouklis_group.parent.connect(andreas_group, {"confidence": 0.5})
    andreas_group.token.connect(andreas, {"order": 0})
    andreas_bougiouklis_group.token.connect(andreas, {"order": 0})
    andreas_bougiouklis_group.token.connect(bougiouklis, {"order": 1})

    return HttpResponse(f"Hello")


def delete_old_nodes():
    for i in Token.nodes.all():
        i.delete()
    for i in Entity.nodes.all():
        i.delete()
    for i in EntitySet.nodes.all():
        i.delete()
