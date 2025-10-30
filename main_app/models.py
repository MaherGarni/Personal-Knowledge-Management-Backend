from django.db import models

class Category(models.Model):
    name   = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    color  = models.CharField(max_length=20, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['parent__id', 'name']   

    @property
    def level(self):
        if not self.parent:
            return 1
        if not self.parent.parent:
            return 2
        return 3


    def __str__(self):
        if self.parent:
            return f"L{self.level}: {self.parent.name} → {self.name}"
        return f"L{self.level}: {self.name}"