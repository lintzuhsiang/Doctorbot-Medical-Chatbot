from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class fb_db(models.Model):
	content = models.TextField()
	time = models.DateTimeField(auto_now_add = True)
	title = models.CharField(max_length=200,default="")
	def publish(self):
		self.published_date = timezone.now()
		self.save()
	def __str__(self):
		return self.title
