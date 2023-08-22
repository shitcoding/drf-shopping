from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

from shopping_list.api.views import (ListAddShoppingItem, ListAddShoppingList,
                                     SearchShoppingItems, ShoppingItemDetail,
                                     ShoppingListAddMembers,
                                     ShoppingListDetail,
                                     ShoppingListRemoveMembers)

urlpatterns = [
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path(
        "api/shopping-lists/",
        ListAddShoppingList.as_view(),
        name="all_shopping_lists",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/",
        ShoppingListDetail.as_view(),
        name="shopping_list_detail",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/add-members/",
        ShoppingListAddMembers.as_view(),
        name="shopping_list_add_members",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/remove-members/",
        ShoppingListRemoveMembers.as_view(),
        name="shopping_list_remove_members",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/shopping-items/",
        ListAddShoppingItem.as_view(),
        name="list_add_shopping_item",
    ),
    path(
        "api/shopping-lists/<uuid:pk>/shopping-items/<uuid:item_pk>/",
        ShoppingItemDetail.as_view(),
        name="shopping_item_detail",
    ),
    path(
        "api/search-shopping-items/",
        SearchShoppingItems.as_view(),
        name="search_shopping_items",
    ),
    # drf-spectacular generated API docs
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
]
