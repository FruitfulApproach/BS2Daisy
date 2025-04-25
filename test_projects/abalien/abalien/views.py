from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect, JsonResponse


def home_page(request):
    context = {}
    return render(request, 'index.html', context=context)