from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from shopping_list.api.pagination import LargeResultsSetPagination
from shopping_list.api.permissions import (
    AllShoppingItemsShoppingListMembersOnly,
    ShoppingItemShoppingListMemberOnly, ShoppingListMembersOnly)
from shopping_list.api.serializers import (AddMemberSerializer,
                                           RemoveMemberSerializer,
                                           ShoppingItemSerializer,
                                           ShoppingListSerializer)
from shopping_list.models import ShoppingItem, ShoppingList


class ListAddShoppingList(generics.ListCreateAPIView):
    """
    Returns the list of all shopping lists user is a member of.
    Each shopping list includes a few unpurchased shopping items.
    Users can add a new shopping list.
    """

    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer

    def perform_create(self, serializer):
        return serializer.save(members=[self.request.user])

    def get_queryset(self):
        return ShoppingList.objects.filter(members=self.request.user).order_by(
            "-last_interaction"
        )


class ShoppingListDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = [ShoppingListMembersOnly]


class ShoppingListAddMembers(APIView):
    permission_classes = [ShoppingListMembersOnly]

    @extend_schema(request=AddMemberSerializer, responses=AddMemberSerializer)
    def put(self, request, pk, format=None):
        shopping_list = ShoppingList.objects.get(pk=pk)
        serializer = AddMemberSerializer(shopping_list, data=request.data)
        self.check_object_permissions(request, shopping_list)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShoppingListRemoveMembers(APIView):
    permission_classes = [ShoppingListMembersOnly]

    @extend_schema(
        request=RemoveMemberSerializer, responses=RemoveMemberSerializer
    )
    def put(self, request, pk, format=None):
        shopping_list = ShoppingList.objects.get(pk=pk)
        serializer = RemoveMemberSerializer(shopping_list, data=request.data)
        self.check_object_permissions(request, shopping_list)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListAddShoppingItem(generics.ListCreateAPIView):
    serializer_class = ShoppingItemSerializer
    permission_classes = [AllShoppingItemsShoppingListMembersOnly]
    pagination_class = LargeResultsSetPagination

    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ["name", "purchased"]

    def get_queryset(self):
        shopping_list = self.kwargs["pk"]
        queryset = ShoppingItem.objects.filter(
            shopping_list=shopping_list
        ).order_by("purchased")

        return queryset


class ShoppingItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer
    permission_classes = [ShoppingItemShoppingListMemberOnly]
    lookup_url_kwarg = "item_pk"


class SearchShoppingItems(generics.ListAPIView):
    serializer_class = ShoppingItemSerializer

    filter_backends = (filters.SearchFilter,)
    search_fields = ["name"]

    def get_queryset(self):
        users_shopping_lists = ShoppingList.objects.filter(
            members=self.request.user
        )
        queryset = ShoppingItem.objects.filter(
            shopping_list__in=users_shopping_lists
        ).order_by("-purchased")
        return queryset
