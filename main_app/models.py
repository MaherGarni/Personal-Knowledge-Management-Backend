from django.db import models

class Category(models.Model):
    name   = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    color  = models.CharField(max_length=20, null=True)
    hierarchy = models.IntegerField()

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['parent__id', 'name']   


    def __str__(self):
        return f"{self.name}"