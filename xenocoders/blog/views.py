from xml.etree.ElementTree import Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from .models import Post, Category, Comment
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from .forms import PostForm, UserProfile
from django.shortcuts import redirect
from .forms import ContactForm, PostForm, CommentForm
from django.contrib import messages


# Create your views here.

class AllPostsView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "all_posts_list"

    def get_context_data(self, *args, **kwargs):

        context = super(AllPostsView, self).get_context_data(*args, **kwargs)
        return context


class CreatePostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    # fields = ["title", "created_on", "text", "status", "category"]
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        form = PostForm()
        context = super(CreatePostView, self).get_context_data(*args, **kwargs)

        context["form"] = form
        return context


class AddCategoryView(CreateView):
    model = Category
    template_name = "blog/add_category.html"
    fields = "__all__"
    success_url = reverse_lazy('home')

 
class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"

    def get_context_data(self, *args, **kwargs):
        form = PostForm()
        
        cat_menu = Post.objects.all()

        context = super(PostDetailView, self).get_context_data(*args, **kwargs)
        context["posts"] = Post.objects.filter(category__name=self.kwargs.get('pk'))

        stuff = get_object_or_404(Post, id=self.kwargs['pk'])

        total_likes = stuff.total_likes()
        cates = stuff.category.all()

        liked = False
        if stuff.likes.filter(id=self.request.user.id).exists():
            liked = True

        context["total_likes"] = total_likes
        context["likes"] = liked
        context["cates"] = cates
        context["form"] = form
        context["cat_menu"] = cat_menu

        return context
        

class PostUpdateView(UpdateView):
    model = Post
    fields = ["title", "text", "status"]


class PostDeleteView(DeleteView):
    model = Post
    template_name = "blog/delete_post.html"
    success_url = reverse_lazy('home')


def CategoryView(request, cates):
    category_posts = Post.objects.filter(category__name=cates)

    context = {
        "category": cates,
        "category_posts": category_posts,
        }

    return render(request, "blog/category.html", context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "New Message on Xenocoders" 
            body = {
            'first_name': form.cleaned_data['first_name'], 
            'email': form.cleaned_data['email_address'], 
            'message':form.cleaned_data['message'], 
            }
            message = "\n".join(body.values())
            
            try:
                send_mail(subject, message, 'hi@imrvon.com', ['hi@imrvon.com']) 
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            messages.success(request, "Message sent." )
            return redirect ("contact")
        messages.error(request, "Error. Message not sent.")

    form = ContactForm()
    return render(request, "blog/contact_us.html", {'form':form})


def about_us(request):
    return render(request, 'blog/about_us.html')

def write_for_us(request):
    return render(request, 'blog/write-for-us.html')

def privacy(request):
    return render(request, 'blog/privacy.html')

def terms(request):
    return render(request, 'blog/terms.html')

def LikeView(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user) 
        liked = True       

    return HttpResponseRedirect(reverse('post', args=[str(pk)]))


class AddCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/add_comment.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)
