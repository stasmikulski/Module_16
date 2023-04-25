from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import *

from datetime import datetime, timedelta
one_week_ago = datetime.today() - timedelta(days=1)


@receiver(m2m_changed, sender=Post.commentPost.through)
def changing_categs(sender, instance, action, **kwargs):
    if action == 'pre_add':
        # This will give you the users BEFORE any removals have happened
        print('pre_add:', instance.commentPost.all())
    elif action == 'post_add':
        # This will give you the users AFTER any removals have happened
        print('post_add:', instance.commentPost.all())
        print('CREATED:', instance.commentPost)
        print(instance.title)
        print(instance.dateCreation)

        email = User.objects.filter(
        ).values_list('email', flat=True)

        subject = f'New comment in post {instance.title}'
        # subject = f'Новая статья в категории {instance.title}'
    
        text_content = (
            f'Заголовок: {instance.title}\n'
            f'Ссылка на статью: http://127.0.0.1:8000{instance.get_absolute_url()}'
        )
        html_content = (
            f'Заголовок: {instance.title}<br>'
            f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
            f'Ссылка на статью</a>'
        )
        for email in emails:
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

