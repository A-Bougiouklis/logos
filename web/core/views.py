# Create your views here.
from django.http import HttpResponse
from .models import *

def home(request):
    return create_coded_nodes()

def create_coded_nodes():
    for i in Token.nodes.all():
        i.delete()

    andreas = Token(lemma="Andreas").save()
    start = Token(lemma="start").save()
    did = Token(lemma="did").save()
    becoming = Token(lemma="becoming").save()
    popular = Token(lemma="popular").save()

    start.nsbuj.connect(andreas, {'something': "Hello"})
    start.aux.connect(did, {'something': "Hello You"})
    start.xcomp.connect(becoming, {'something': "Hello You"})
    becoming.acomp.connect(popular, {'something': "Hello You"})

    return HttpResponse(f"{len(andreas.nodes.all())} {andreas} {start} {andreas.nsbuj.is_connected(start)}")
