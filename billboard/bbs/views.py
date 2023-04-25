from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import *
from .filters import PostFilter
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.core.cache import cache
from django.http import HttpResponse
from django.views import View
#from .tasks import hello, my_job

class IndexView(View):
    def get(self, request):
        my_job.delay()
        hello.delay()
        return HttpResponse('Hello!')

# Create your views here.
def index(request):
    bbs = Post.objects.all().order_by("dateCreation").reverse()[:5]
    # bbs = Post.objects.all().order_by("-id")
    categories = Category.objects.all()
    return render(request, 'index.html', context={'bbs': bbs, 'categories': categories})

def detail(request, id):
    new = Post.objects.get(id=id)
    post_comments = Comment.objects.filter(commentPost=Post.objects.get(id=id))
    ####post_comments_count = Comment.objects.filter(commentPost=Post.objects.get(id=id)).count()
    #post_comments_values = post_comments.values('dateCreation', 'commentUser', 'rating', 'text')
    #print(post_comments_values)
    return render(request, 'details.html', context={'new': new, 'post_comments': post_comments})


class PostList(ListView):
   model = Post
   ordering = '-dateCreation'
   template_name = 'bbs_list_all.html'
   context_object_name = 'bbs'
   paginate_by = 5


class PostSearch(ListView):
   model = Post
   ordering = '-dateCreation'
   template_name = 'search.html'
   context_object_name = 'bbs'
   paginate_by = 5

   # Переопределяем функцию получения списка новостей
   def get_queryset(self):
       # Получаем обычный запрос
       queryset = super().get_queryset()
       # Используем наш класс фильтрации.
       # self.request.GET содержит объект QueryDict, который мы рассматривали
       # в этом юните ранее.
       # Сохраняем нашу фильтрацию в объекте класса,
       # чтобы потом добавить в контекст и использовать в шаблоне.
       self.filterset = PostFilter(self.request.GET, queryset)
       # Возвращаем из функции отфильтрованный список новостей
       return self.filterset.qs

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       # Добавляем в контекст объект фильтрации.
       context['filterset'] = self.filterset
       return context


class PostbyCategList(ListView):
   model = Post
   template_name = 'bbs_list.html'
   context_object_name = 'bbs'
   paginate_by = 5

   def get_queryset(self):
       return Post.objects.filter(categoryType=self.kwargs['slug']).order_by("dateCreation").reverse()


def postbycategory(request, slug):
    qs = Post.objects.filter(categoryType=slug).order_by("dateCreation").reverse()
    categories = Category.objects.all()
    return render(request, 'bbs_list.html', {'bbs': qs, 'categories': categories, 'slugname': slug})


class PostDetail(DetailView):
   model = Post
   template_name = 'detail.html'
   context_object_name = 'new'
   queryset = Post.objects.all()


class PostDetailEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ('bbs.change_post',)
    form_class = PostForm
    model = Post
    context_object_name = 'new'
    template_name = 'post_edit.html'

    def form_valid(self, form):
        # post = form.save(commit=False)
        # post.categoryType = 'AR'
        # Это если будет нужно сменить 'NW' на 'AR'
        form.save()
        return super(PostDetailEdit, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse('post_detail_show', kwargs={'id': self.object.pk})


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('bbs.delete_post',)
    model = Post
    context_object_name = 'new'
    template_name = 'post_delete.html'
    success_url = '/bbs_list/'


def create_post(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            #form.save()
            return HttpResponseRedirect('/bbs_list/')
    return render(request, 'post_edit.html', {'form': form})


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('bbs.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'

    def form_valid(self, form):
        userid = self.request.user.id
        post = form.save(commit=False)
        post.author = Author.objects.get(id=userid)
        form.save(commit=False)
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        # print('* * * * * * *', self.object.pk)
        return reverse('post_detail_show', kwargs={'id': self.object.pk})


@csrf_protect
@permission_required('bbs.add_comment',)
def comment_create_view(request, pk):
    #print('- - -comment_create_view- - >', pk)
    new = Post.objects.get(id=pk)
    #print('New:', new)
    if request.method == 'GET':
        #print('GET - - - >', pk)
        comment_form = CommentForm()
        context = {
            'new': new,
            'comment_form': comment_form,
        }
        return render(request, 'comment_create.html', context)

    elif request.method == 'POST':
        #print('POST - - - >', pk)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            #print('POST - - - >form.is_valid', pk)
            #commentUser = comment_form.cleaned_data.get('commentUser')
            commentUser = request.user
            text = comment_form.cleaned_data.get('text')
            Comment.objects.create(
                commentPost=new,
                commentUser=commentUser,
                text=text
            )
            context = {
                'new': new,
                'comment_form': comment_form,
            }
            return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': pk}))
        else:
            context = {
                'new': new,
                'comment_form': comment_form,
            }
            return render(request, 'comment_create.html', context)


@csrf_protect
@permission_required('bbs.change_comment',)
def comment_edit_view(request, id1, id2):
    #print('- - - comment_edit_view - - new:', id1, '- - comment:', id2)
    new = Post.objects.get(id=id1)
    #print('New:', new)
    comment = Comment.objects.get(id=id2)
    #print('Comment:', comment)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': id1}))
    return render(request, 'comment_edit.html', {'new': new, 'comment': comment, 'form': form})


class CommentDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('bbs.delete_comment',)
    #model = Comment
    template_name = 'comment_delete.html'
    success_url = '/bbs_list/'

    def get_object(self):
        #print('get_object')
        #print('- - - comment_delete_view - - new:', id1, '- - comment:', id2)
        new = Post.objects.get(id=self.kwargs['id1'])
        #print('New:', new)
        idid1 = new.id
        #print('idid1',idid1)
        comment = Comment.objects.get(id=self.kwargs['id2'])
        #print('Comment:', comment)
        idid2 = comment.id
        #print('idid2',idid2)
        context = {'new': new, 'comment': comment}
        return comment
        #TODO надо передать и new и comment, но передается только comment, а context ничего не перадает (пусто)

    def delete(self, request, *args, **kwargs):
        comment2del = Comment.objects.get(id=self.kwargs['id2'])
        comment2del.delete()
        return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': id1}))


@csrf_protect
@permission_required('bbs.delete_comment',)
def comment_delete_view(request, id1, id2):
    #print('- - - comment_delete_view - - new:', id1, '- - comment:', id2)
    new = Post.objects.get(id=id1)
    #print('New:', new)
    comment = Comment.objects.get(id=id2)
    #print('Comment:', comment)
    if request.method == 'POST':
        #print('- - - form valid - - new:', id1, '- - comment:', id2)
        comment2del = Comment.objects.get(id=id2)
        comment2del.delete()
        return HttpResponseRedirect(reverse('post_detail_show', kwargs={'id': id1}))
    else:
        #No data submitted; create a blank form.
        form = CommentForm()
    return render(request, 'comment_delete.html', {'new': new, 'comment': comment})


class ContactList(ListView):
    model = Post
    ordering = '-dateCreation'
    template_name = 'bbs_list.html'
    context_object_name = 'bbs'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        print(user)
        if user.is_authenticated:
            print(user, 'is_authenticated')
            return Post.objects.filter(author=self.request.user)
        return Post.objects.filter(author=None)


@login_required
@csrf_protect
def MyPostList(request):
    qs = Post.objects.filter(author=request.user.id).order_by("dateCreation").reverse()
    return render(request, 'bbs_list_all_my.html', {'bbs': qs})

@login_required
@csrf_protect
def MyCommentList(request):
    #_qs = Comment.objects.filter(post__author=user)
    qs = Comment.objects.filter(commentUser=request.user.id)
    print(qs)
    #.order_by("dateCreation").reverse()
    return render(request, 'comment_all_my.html', {'comments': qs})


@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        print(category_id)
        category = Category.objects.get(id=category_id)
        print(category)
        action = request.POST.get('action')
        print(action)

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )