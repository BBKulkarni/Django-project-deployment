# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from django.views import generic
from groups.models import Group
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from braces.views import SelectRelatedMixin

from . import models
from posts.models import Post, Vote
from . import forms

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.


class PostList(SelectRelatedMixin,generic.ListView):
    model = models.Post
    select_related = ('user', 'group')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_groups"] = Group.objects.filter(members__in=[self.request.user])
        context["all_groups"] = Group.objects.all()
        return context


class UserPost(generic.ListView):
    model = models.Post
    template_name = 'posts/user_post_list.html'

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related('posts').get(username__iexact=self.kwargs.get('username'))

        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_user"] = self.post_user
        return context


class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ('user', 'group')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))


class CreatePost(LoginRequiredMixin,SelectRelatedMixin,generic.CreateView):
    fields = ('message','group')
    model = models.Post

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class DeletePost(LoginRequiredMixin,SelectRelatedMixin,generic.DeleteView):
    model = models.Post
    select_related = ('user', 'group')
    success_url = reverse_lazy('posts:all')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Post deleted')
        return super().delete(*args, **kwargs)


class Downvote(LoginRequiredMixin, generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        # return reverse('posts:single', kwargs={'pk': self.kwargs.get('pk')})
        return reverse_lazy('posts:all')

    def get(self, request, *args, **kwargs):
        try:
            votes = models.Vote.objects.filter(
                user=self.request.user, post__pk=self.kwargs.get('pk')
            ).get()

        except models.Vote.DoesNotExist:
            messages.warning(self.request, 'Sorry you are not allowed for the operation')
        else:
            votes.delete()
        return super().get(self.request, *args, **kwargs)


class Upvote(LoginRequiredMixin,generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        # return reverse('posts:single', kwargs={'pk': self.kwargs.get('pk')})
        return reverse_lazy('posts:all')

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))

        try:
            Vote.objects.create(user=self.request.user, post=post)
        except IntegrityError:
            messages.warning(self.request, 'Already voted')
        else:
            messages.success(self.request, 'Voted!')
        return super().get(self.request, *args, **kwargs)




