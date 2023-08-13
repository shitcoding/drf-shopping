from datetime import datetime, timedelta
from unittest import mock

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from shopping_list.models import ShoppingItem, ShoppingList


@pytest.mark.django_db
def test_valid_shopping_list_is_created(
    create_user, create_authenticated_client
):
    url = reverse("all_shopping_lists")
    data = {
        "name": "Groceries",
    }
    client = create_authenticated_client(create_user())
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.get().name == "Groceries"


@pytest.mark.django_db
def test_shopping_list_name_missing_returns_bad_request(
    create_user, create_authenticated_client
):
    url = reverse("all_shopping_lists")
    data = {
        "kek": "kekek",
    }
    client = create_authenticated_client(create_user())
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_all_shopping_lists_are_listed(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    url = reverse("all_shopping_lists")
    create_shopping_list(user, "Groceries")
    create_shopping_list(user, "Books")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    assert response.data["results"][0]["name"] == "Books"
    assert response.data["results"][1]["name"] == "Groceries"


@pytest.mark.django_db
def test_shopping_list_is_retrieved_by_id(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user, "Groceries")

    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"


@pytest.mark.django_db
def test_shopping_list_includes_only_corresponding_items(
    create_user, create_shopping_list, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)

    shopping_list1 = create_shopping_list(user, "Groceries")
    shopping_list2 = create_shopping_list(user, "Books")

    ShoppingItem.objects.create(
        shopping_list=shopping_list1, name="Eggs", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list2, name="War and Peace", purchased=False
    )

    url = reverse("shopping_list_detail", args=[shopping_list1.id])
    response = client.get(url)

    assert len(response.data["unpurchased_items"]) == 1
    assert response.data["unpurchased_items"][0]["name"] == "Eggs"


@pytest.mark.django_db
def test_shopping_list_name_is_changed(
    create_user, create_shopping_list, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user, "Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "name": "Food",
    }

    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"


@pytest.mark.django_db
def test_shopping_list_not_changed_because_name_is_missing(
    create_user, create_shopping_list, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user, "Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "kek": "kekek",
    }

    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_list_name_is_changed_with_partial_update(
    create_user, create_shopping_list, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user, "Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "name": "Food",
    }

    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"


@pytest.mark.django_db
def test_shopping_list_partial_update_with_missing_name_has_no_impact(
    create_user, create_shopping_list, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user, "Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "kek": "kekek",
    }

    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"


@pytest.mark.django_db
def test_shopping_list_is_deleted(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingList.objects.all()) == 0


# Testing permissions


@pytest.mark.django_db
def test_update_shopping_list_restricted_if_not_member(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    shopping_list_creator = User.objects.create_user(
        "Creator", "creator@kekek.kek", "kekek"
    )
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(shopping_list_creator)
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "name": "Food",
    }
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_partial_update_shopping_list_restricted_if_not_member(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    shopping_list_creator = User.objects.create_user(
        "Creator", "creator@kekek.kek", "kekek"
    )
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(shopping_list_creator)
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "name": "Food",
    }
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_shopping_list_restricted_if_not_member(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    shopping_list_creator = User.objects.create_user(
        "Creator", "creator@kekek.kek", "kekek"
    )
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(shopping_list_creator)
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.delete(url, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_retrieve_shopping_list(
    create_user,
    create_shopping_list,
    admin_client,
):
    user = create_user()
    shopping_list = create_shopping_list(user)
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = admin_client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_client_retrieves_only_lists_they_are_member_of(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    shopping_list = ShoppingList.objects.create(name="Books")
    shopping_list.members.add(user)

    user2 = User.objects.create_user("User2", "user2@kekek.kek", "kekek")
    create_shopping_list(user2)

    client = create_authenticated_client(user)
    url = reverse("all_shopping_lists")
    response = client.get(url)

    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Books"


@pytest.mark.django_db
def test_correct_order_of_shopping_lists(
    create_user,
    create_authenticated_client,
):
    url = reverse("all_shopping_lists")
    user = create_user()
    client = create_authenticated_client(user)

    old_time = datetime.now() - timedelta(days=1)
    older_time = datetime.now() - timedelta(days=100)

    with mock.patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = old_time
        ShoppingList.objects.create(name="Old").members.add(user)

        mock_now.return_value = older_time
        ShoppingList.objects.create(name="Older").members.add(user)

    ShoppingList.objects.create(name="New").members.add(user)

    response = client.get(url)

    assert response.data["results"][0]["name"] == "New"
    assert response.data["results"][1]["name"] == "Old"
    assert response.data["results"][2]["name"] == "Older"


@pytest.mark.django_db
def test_lists_order_changed_when_item_marked_purchased(
    create_user,
    create_authenticated_client,
):
    user = create_user()
    client = create_authenticated_client(user)

    recent_time = datetime.now() - timedelta(days=1)
    older_time = datetime.now() - timedelta(days=20)

    with mock.patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = older_time
        older_list = ShoppingList.objects.create(name="Older")
        older_list.members.add(user)
        item_in_older_list = ShoppingItem.objects.create(
            name="Milk", purchased=False, shopping_list=older_list
        )

        mock_now.return_value = recent_time
        ShoppingList.objects.create(
            name="Recent",
            last_interaction=datetime.now() - timedelta(days=100),
        ).members.add(user)

        shopping_item_url = reverse(
            "shopping_item_detail",
            kwargs={"pk": older_list.id, "item_pk": item_in_older_list.id},
        )
        shopping_lists_url = reverse("all_shopping_lists")

        data = {"purchased": True}

        client.patch(shopping_item_url, data)

        response = client.get(shopping_lists_url)

        assert response.data["results"][1]["name"] == "Recent"
        assert response.data["results"][0]["name"] == "Older"
