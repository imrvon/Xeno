from django.urls import path
from .views import contact, about_us, write_for_us, privacy, terms, AllPostsView, CreatePostView, PostDetailView, PostUpdateView, PostDeleteView, AddCategoryView, CategoryView, LikeView, AddCommentView
from .forms import ContactForm
from . import views


urlpatterns = [
    path('', AllPostsView.as_view(), name="home"),
    path('add_post/', CreatePostView.as_view(), name="add_post"),
    path('post/<int:pk>/', PostDetailView.as_view(), name="post"),
    path('post/edit/<int:pk>/', PostUpdateView.as_view(), name="update_post"),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name="delete_post"),
    path('contact_us/', views.contact, name="contact"),
    path('add_category/', AddCategoryView.as_view(), name="add_category"),
    path('category/<str:cates>/', CategoryView, name="category"),
    path('about_us/', about_us, name="about_us"),
    path('write-for-us/', write_for_us, name="write-for-us"),
    path('privacy/', privacy, name="privacy"),
    path('terms/', terms, name="terms"),
    path('like/<int:pk>', LikeView, name="like_post"),
    path('post/<int:pk>/comment', AddCommentView.as_view(), name="add_comment")
]