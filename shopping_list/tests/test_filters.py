import pytest
from django.urls import reverse

from shopping_list.models import ShoppingItem, User


@pytest.mark.django_db
def test_search_returns_correct_item(
    create_user, create_authenticated_client, create_shopping_item
):
    user = create_user()
    client = create_authenticated_client(user)

    create_shopping_item(user, "Chocolate")
    create_shopping_item(user, "Skim Milk")

    search_param = "?search=milk"
    url = reverse("search_shopping_items") + search_param

    response = client.get(url)

    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Skim Milk"


@pytest.mark.django_db
def test_search_returns_only_users_items(
    create_user, create_authenticated_client, create_shopping_item
):
    user = create_user()
    client = create_authenticated_client(user)
    user2 = User.objects.create_user("User2", "user2@kekek.kek", "kekek")

    create_shopping_item(user, "Milk")
    create_shopping_item(user2, "Milk")

    search_param = "?search=milk"
    url = reverse("search_shopping_items") + search_param

    response = client.get(url)

    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_order_shopping_items_names_ascending(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)

    ShoppingItem.objects.create(
        name="Bananas", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Coconut", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )

    order_param = "?ordering=name"
    url = (
        reverse("list_add_shopping_item", args=[shopping_list.id])
        + order_param
    )

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Apples"
    assert response.data["results"][1]["name"] == "Bananas"
    assert response.data["results"][2]["name"] == "Coconut"


@pytest.mark.django_db
def test_order_shopping_items_names_descending(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)

    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Coconut", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Bananas", purchased=False, shopping_list=shopping_list
    )

    order_param = "?ordering=-name"
    url = (
        reverse("list_add_shopping_item", args=[shopping_list.id])
        + order_param
    )

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Coconut"
    assert response.data["results"][1]["name"] == "Bananas"
    assert response.data["results"][2]["name"] == "Apples"


@pytest.mark.django_db
def test_order_shopping_items_unpurchased_first(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)

    ShoppingItem.objects.create(
        name="Bananas", purchased=True, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )

    order_param = "?ordering=purchased"
    url = (
        reverse("list_add_shopping_item", args=[shopping_list.id])
        + order_param
    )

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Apples"
    assert response.data["results"][1]["name"] == "Bananas"


@pytest.mark.django_db
def test_order_shopping_items_unpurchased_first(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)

    ShoppingItem.objects.create(
        name="Bananas", purchased=True, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )

    order_param = "?ordering=purchased"
    url = (
        reverse("list_add_shopping_item", args=[shopping_list.id])
        + order_param
    )

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Apples"
    assert response.data["results"][1]["name"] == "Bananas"


@pytest.mark.django_db
def test_order_shopping_items_purchased_first(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)

    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Bananas", purchased=True, shopping_list=shopping_list
    )

    order_param = "?ordering=-purchased"
    url = (
        reverse("list_add_shopping_item", args=[shopping_list.id])
        + order_param
    )

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Bananas"
    assert response.data["results"][1]["name"] == "Apples"


@pytest.mark.django_db
def test_order_shopping_items_by_purchased_and_names(
    create_user,
    create_authenticated_client,
    create_shopping_list,
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)

    ShoppingItem.objects.create(
        name="Apples", purchased=True, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Bananas", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Coconut", purchased=True, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Dates", purchased=False, shopping_list=shopping_list
    )

    order_param = "?ordering=purchased,name"
    url = (
        reverse("list_add_shopping_item", args=[shopping_list.id])
        + order_param
    )

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Bananas"
    assert response.data["results"][1]["name"] == "Dates"
    assert response.data["results"][2]["name"] == "Apples"
    assert response.data["results"][3]["name"] == "Coconut"
