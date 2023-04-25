from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
   class Meta:
       model = Post
       #fields = '__all__'
       fields = [
           #'author',
           'categoryType',
           'title',
           'text',
       ]

class CommentForm(forms.ModelForm):
   class Meta:
       model = Comment
       #fields = '__all__'
       fields = [
           #'commentUser',
           'text',
       ]