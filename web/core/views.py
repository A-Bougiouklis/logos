# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from neomodel import RelationshipTo, StructuredNode, StringProperty, RelationshipDefinition, EITHER
from neomodel.contrib import SemiStructuredNode

def home(request):
    # book = Book(title="Harry", format="A", status="A").save()
    # shelf = Shelf(name="cool").save()
    # return HttpResponse(f"Hello")
    return create_dynamically_nodes()

def create_coded_nodes():
    andreas = Person(name="Andreas", age=1).save()
    greece = Country(code="Germany").save()
    andreas.country.connect(greece)
    return HttpResponse(f"{len(andreas.nodes.all())} {andreas} {greece} {andreas.country.is_connected(greece)}")



# Create two Structured Nodes
country = type(
    "Country_1",
    (SemiStructuredNode,),
    {"name": StringProperty()}
)
person = type(
    "Person_1",
    (SemiStructuredNode,),
    {
        "name": StringProperty(),
        "is_from": RelationshipTo(country, 'IS_FROM')
    }
)

def create_dynamically_nodes():

    # Now we need to create an object of that class
    nikola = person(name="Nikola Tesla").save()
    greece = country(name="Greece").save()

    # create property on the fly
    greece.skata = "5"
    greece.save()

    europe = country(name="Europe").save()

    nikola.is_from.connect(greece)

    return HttpResponse(f"{len(nikola.nodes.all())} {nikola} {greece.skata} {nikola.is_from.is_connected(greece)}")
