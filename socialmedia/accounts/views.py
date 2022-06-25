from django.shortcuts import render
from django.contrib.auth import login, logout
# from django.core.urlresolvers import reverse_lazy
from django.urls import reverse_lazy
from django.views.generic import CreateView

from . import forms

from . import models
# Create your views here.

class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'
