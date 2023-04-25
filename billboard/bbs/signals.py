from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import *

from datetime import datetime, timedelta
one_week_ago = datetime.today() - timedelta(days=1)



@receiver(post_save, sender=Comment)
def comment_created(instance, created, **kwargs):
    if not created:
        return
    if created:
        print('Comment CREATED:')
        #print(instance.text)
        #print(instance.dateCreation)
        #print(instance.commentPost)
        #print(instance.commentPost.id)
        #print(instance.commentPost.title)
        #print(instance.commentUser)
        #print(instance.commentUser.id)
        #print(instance.commentUser.email)

        user = instance.commentUser
        user_email = instance.commentUser.email
        print(user, user_email)

        email = user_email

        subject = f'New comment in post {instance.commentPost.title}'
        # subject = f'Новый комментарий к статье {instance.commentPost.title}'
    
        text_content = (
            f'Заголовок: {instance.commentPost.title}\n'
            f'Ссылка на статью: http://127.0.0.1:8000{instance.commentPost.get_absolute_url()}'
        )
        html_content = (
            f'Заголовок: {instance.commentPost.title}<br>'
            f'<a href="http://127.0.0.1:8000{instance.commentPost.get_absolute_url()}">'
            f'Ссылка на статью</a>'
        )
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


