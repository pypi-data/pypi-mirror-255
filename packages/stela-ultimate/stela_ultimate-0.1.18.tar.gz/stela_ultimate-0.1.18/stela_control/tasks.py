from django.utils import timezone
from .models import Content

def schedule_blogpost():
    bulk_post=Content.objects.filter(is_schedule=True)
    current_time = timezone.now()
    if bulk_post.exists():
        for post in bulk_post:
            if current_time > post.schedule:
                post.status = 'Publish'
                post.save()
    else:
        pass

def task2():
    return