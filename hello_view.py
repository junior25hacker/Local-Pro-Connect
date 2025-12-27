from django.shortcuts import render
from .models import Person

def hello_view(request):
    people = Person.objects.all()
    return render(request, 'hello/hello.html', {'people': people})