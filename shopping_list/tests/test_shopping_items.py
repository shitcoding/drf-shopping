import pytest
from django.urls import reverse
from rest_framework import status

from shopping_list.models import ShoppingItem, ShoppingList, User


@pytest.mark.django_db
def test_valid_shopping_item_is_created(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user, "Groceries")
    url = reverse("list_add_shopping_item", args=[shopping_list.id])
    data = {
        "name": "Milk",
        "purchased": False,
    }
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_shopping_item_missing_data_returns_bad_request(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user, "Groceries")
    url = reverse("list_add_shopping_item", args=[shopping_list.id])
    data = {
        "name": "Milk",
    }
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_item_is_retrieved_by_id(
    create_shopping_item, create_user, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Chocolate"


@pytest.mark.django_db
def test_change_shopping_item_purchased_status(
    create_shopping_item, create_user, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    data = {
        "name": "Chocolate",
        "purchased": True,
    }
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_missing_data_returns_bad_request(
    create_shopping_item, create_user, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    data = {
        "purchased": True,
    }
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_partial_update(
    create_shopping_item, create_user, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    data = {
        "purchased": True,
    }
    response = client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True


@pytest.mark.django_db
def test_shopping_item_is_deleted(
    create_shopping_item, create_user, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingItem.objects.all()) == 0


@pytest.mark.django_db
def test_not_member_of_list_cannot_add_shopping_item(
    create_shopping_list, create_user, create_authenticated_client
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user(
        "Creator", "creator@kekek.kek", "kekek"
    )
    shopping_list = create_shopping_list(shopping_list_creator)

    url = reverse("list_add_shopping_item", args=[shopping_list.id])
    data = {
        "name": "Milk",
        "purchased": False,
    }

    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_add_shopping_items(
    create_user, create_shopping_list, admin_client
):
    user = create_user()
    shopping_list = create_shopping_list(user)

    url = reverse("list_add_shopping_item", kwargs={"pk": shopping_list.id})
    data = {
        "name": "Milk",
        "purchased": False,
    }

    response = admin_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert len(ShoppingItem.objects.all()) == 1


@pytest.mark.django_db
def test_shopping_item_detail_restricted_if_not_member_of_list(
    create_user, create_authenticated_client, create_shopping_item
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user(
        "Creator", "creator@kekek.kek", "kekek"
    )
    shopping_item = create_shopping_item(
        name="Chocolate", user=shopping_list_creator
    )

    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )
    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_shopping_item_update_restricted_if_not_member_of_list(
    create_user,
    create_authenticated_client,
    create_shopping_item,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user(
        "Creator", "creator@kekek.kek", "kekek"
    )
    shopping_item = create_shopping_item(
        name="Chocolate", user=shopping_list_creator
    )
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )

    data = {
        "name": "Chocolate",
        "purchased": True,
    }

    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_shopping_item_partial_update_restricted_if_not_member_of_list(
    create_user,
    create_authenticated_client,
    create_shopping_item,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user(
        "Creator", "creator@kekek.kek", "kekek"
    )
    shopping_item = create_shopping_item(
        name="Chocolate", user=shopping_list_creator
    )
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )

    data = {
        "purchased": True,
    }

    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_shopping_item_delete_restricted_if_not_member_of_list(
    create_user,
    create_authenticated_client,
    create_shopping_item,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user(
        "Creator", "creator@kekek.kek", "kekek"
    )
    shopping_item = create_shopping_item(
        name="Chocolate", user=shopping_list_creator
    )
    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )

    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_retrieve_single_shopping_item(
    create_user,
    create_shopping_item,
    admin_client,
):
    user = create_user()
    shopping_item = create_shopping_item(user, "Chocolate")

    url = reverse(
        "shopping_item_detail",
        kwargs={
            "pk": shopping_item.shopping_list.id,
            "item_pk": shopping_item.id,
        },
    )

    response = admin_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_items_are_retrieved_by_list_member(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    shopping_list = create_shopping_list(user)

    shopping_item1 = ShoppingItem.objects.create(
        name="Oranges", purchased=False, shopping_list=shopping_list
    )
    shopping_item2 = ShoppingItem.objects.create(
        name="Milk", purchased=False, shopping_list=shopping_list
    )

    client = create_authenticated_client(user)
    url = reverse("list_add_shopping_item", kwargs={"pk": shopping_list.id})
    response = client.get(url)

    assert len(response.data["results"]) == 2
    assert response.data["results"][0]["name"] == shopping_item1.name
    assert response.data["results"][1]["name"] == shopping_item2.name


@pytest.mark.django_db
def test_list_items_are_not_retrieved_by_not_list_member(
    create_user, create_authenticated_client, create_shopping_item
):
    list_creator = User.objects.create_user(
        "creator",
        "creator@kekek.kek",
        "kekek",
    )
    shopping_item = create_shopping_item(list_creator, "Milk")

    user = create_user()
    client = create_authenticated_client(user)
    url = reverse(
        "list_add_shopping_item", kwargs={"pk": shopping_item.shopping_list.id}
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_items_only_from_the_same_shopping_list(
    create_user,
    create_authenticated_client,
    create_shopping_list,
    create_shopping_item,
):
    user = create_user()

    shopping_list1 = ShoppingList.objects.create(name="List1")
    shopping_list1.members.add(user)
    shopping_item_from_list1 = ShoppingItem.objects.create(
        name="Oranges", purchased=False, shopping_list=shopping_list1
    )

    shopping_list2 = ShoppingList.objects.create(name="List2")
    shopping_list2.members.add(user)
    shopping_item_from_list2 = ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list2
    )

    client = create_authenticated_client(user)
    url = reverse("list_add_shopping_item", kwargs={"pk": shopping_list1.id})

    response = client.get(url)

    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == shopping_item_from_list1.name


@pytest.mark.django_db
def test_max_3_items_in_shopping_list(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)

    shopping_list = create_shopping_list(user)

    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Eggs", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Milk", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Chocolate", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Mango", purchased=False
    )

    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.get(url, format="json")

    assert len(response.data["unpurchased_items"]) == 3


@pytest.mark.django_db
def test_all_items_in_shopping_list_are_unpurchased(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)

    shopping_list = create_shopping_list(user)

    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Eggs", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Milk", purchased=True
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Chocolate", purchased=False
    )

    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.get(url, format="json")

    assert len(response.data["unpurchased_items"]) == 2


@pytest.mark.django_db
def test_adding_duplicate_item_raises_bad_request(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)

    shopping_list = create_shopping_list(user)
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Milk", purchased=False
    )

    url = reverse("list_add_shopping_item", args=[shopping_list.id])

    data = {
        "name": "Milk",
        "purchased": False,
    }

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(shopping_list.shopping_items.all()) == 1
