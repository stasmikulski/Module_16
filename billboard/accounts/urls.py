from django.urls import path
from .views import SignUp

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    #path('login/', user_login, name='userlogin'),

]