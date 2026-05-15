from django.db import models
from django.contrib.auth.models import User
    
class Category(models.Model):
    name   = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    color  = models.CharField(max_length=20, null=True)
    hierarchy = models.IntegerField()
    rating = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    

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
    points = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-updated_at']
    def __str__(self):
        return f"{self.title}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    daily_ai_limit = models.IntegerField(default=5) 
    daily_calls_counter = models.IntegerField(default=0)
    max_reached_date = models.DateTimeField(null=True, blank=True)

class UserCategoryScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="user_scores")
    aggregated_score = models.FloatField(default=0)
    lesson_scores = models.JSONField(default=list)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'category')

