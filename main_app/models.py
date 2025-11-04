from django.db import models
from django.contrib.auth.models import User
    
class Category(models.Model):
    name   = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    color  = models.CharField(max_length=20, null=True)
    hierarchy = models.IntegerField()
    

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['-parent__id', 'name']   


    def __str__(self):
        return f"{self.name}"
    
class Lesson(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-updated_at']
    def __str__(self):
        return f"{self.title}"