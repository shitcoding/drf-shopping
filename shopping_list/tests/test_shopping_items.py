import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shopping_list.models import ShoppingItem, ShoppingList
from shopping_list.tests.fixtures import create_shopping_item


@pytest.mark.django_db
def test_valid_shopping_item_is_created():
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("add_shopping_item", args=[shopping_list.id])
    data = {
        "name": "Milk",
        "purchased": False,
    }
    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_shopping_item_missing_data_returns_bad_request():
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("add_shopping_item", args=[shopping_list.id])
    data = {
        "name": "Milk",
    }
    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_item_is_retrieved_by_id(create_shopping_item):
    shopping_item = create_shopping_item(name="Chocolate")
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    client = APIClient()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Chocolate"


@pytest.mark.django_db
def test_change_shopping_item_purchased_status(create_shopping_item):
    shopping_item = create_shopping_item(name="Chocolate")
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    client = APIClient()
    data = {
        "name": "Chocolate",
        "purchased": True,
    }
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_missing_data_returns_bad_request(
    create_shopping_item,
):
    shopping_item = create_shopping_item(name="Chocolate")
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    client = APIClient()
    data = {
        "purchased": True,
    }
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_partial_update(
    create_shopping_item,
):
    shopping_item = create_shopping_item(name="Chocolate")
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    client = APIClient()
    data = {
        "purchased": True,
    }
    response = client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True


@pytest.mark.django_db
def test_shopping_item_is_deleted(create_shopping_item):
    shopping_item = create_shopping_item(name="Chocolate")
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    client = APIClient()
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingItem.objects.all()) == 0
