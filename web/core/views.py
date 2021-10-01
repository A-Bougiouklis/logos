# Create your views here.
from django.http import HttpResponse
from .models import *

def home(request):
    return create_coded_nodes()

def create_coded_nodes():

    delete_old_nodes()

    andreas = Token(lemma="Andreas").save()
    bougiouklis = Token(lemma="Bougiouklis").save()
    start = Token(lemma="start").save()
    did = Token(lemma="did").save()
    becoming = Token(lemma="becoming").save()
    popular = Token(lemma="popular").save()

    start.nsbuj.connect(andreas, {'something': "Hello"})
    start.aux.connect(did, {'something': "Hello You"})
    start.xcomp.connect(becoming, {'something': "Hello You"})
    becoming.acomp.connect(popular, {'something': "Hello You"})
    andreas.acomp.connect(bougiouklis, {'something': "Hello You"})

    andreas_group = Group(name="Andreas").save()
    andreas_bougiouklis_group = Group(name="Andreas Bougiouklis").save()

    andreas_group.subgroup.connect(andreas_bougiouklis_group)
    andreas_group.token.connect(andreas, {"order": 0})
    andreas_bougiouklis_group.token.connect(andreas, {"order": 0})
    andreas_bougiouklis_group.token.connect(bougiouklis, {"order": 1})

    return HttpResponse(f"{len(andreas.nodes.all())} {andreas} {start} {andreas.nsbuj.is_connected(start)}")

def delete_old_nodes():
    for i in Token.nodes.all():
        i.delete()
    for i in Group.nodes.all():
        i.delete()
