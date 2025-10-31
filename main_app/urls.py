from django.urls import path
from .views import Home, CategoriesIndex

urlpatterns = [
    path('', Home.as_view(), name='home'), #comment
    path('categories/', CategoriesIndex.as_view(), name='categories-index'),
]