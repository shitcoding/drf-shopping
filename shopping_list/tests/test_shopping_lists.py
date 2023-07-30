import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shopping_list.models import ShoppingItem, ShoppingList


@pytest.mark.django_db
def test_valid_shopping_list_is_created():
    url = reverse("all_shopping_lists")
    data = {
        "name": "Groceries",
    }
    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.get().name == "Groceries"


@pytest.mark.django_db
def test_shopping_list_name_missing_returns_bad_request():
    url = reverse("all_shopping_lists")
    data = {
        "kek": "kekek",
    }
    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_all_shopping_lists_are_listed():
    url = reverse("all_shopping_lists")
    ShoppingList.objects.create(name="Groceries")
    ShoppingList.objects.create(name="Books")

    client = APIClient()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]["name"] == "Groceries"
    assert response.data[1]["name"] == "Books"


@pytest.mark.django_db
def test_shopping_list_is_retrieved_by_id():
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    client = APIClient()
    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"


@pytest.mark.django_db
def test_shopping_list_includes_only_corresponding_items():
    shopping_list1 = ShoppingList.objects.create(name="Groceries")
    shopping_list2 = ShoppingList.objects.create(name="Books")

    ShoppingItem.objects.create(
        shopping_list=shopping_list1, name="Eggs", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list2, name="War and Peace", purchased=False
    )

    url = reverse("shopping_list_detail", args=[shopping_list1.id])
    client = APIClient()
    response = client.get(url)

    assert len(response.data["shopping_items"]) == 1
    assert response.data["shopping_items"][0]["name"] == "Eggs"


@pytest.mark.django_db
def test_shopping_list_name_is_changed():
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "name": "Food",
    }

    client = APIClient()
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"


@pytest.mark.django_db
def test_shopping_list_not_changed_because_name_is_missing():
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "kek": "kekek",
    }

    client = APIClient()
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_list_name_is_changed_with_partial_update():
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "name": "Food",
    }

    client = APIClient()
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"


@pytest.mark.django_db
def test_shopping_list_partial_update_with_missing_name_has_no_impact():
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "kek": "kekek",
    }

    client = APIClient()
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"


@pytest.mark.django_db
def test_shopping_list_is_deleted():
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    client = APIClient()
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingList.objects.all()) == 0
