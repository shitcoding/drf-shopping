from django.urls import include, path
from rest_framework import routers

from shopping_list.api.viewsets import ShoppingItemViewset

router = routers.DefaultRouter()
router.register(
    "shopping-items", ShoppingItemViewset, basename="shopping-items"
)

urlpatterns = [
    path("api/", include(router.urls)),
]
