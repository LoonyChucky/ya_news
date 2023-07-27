import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',  
    ('news:home', 
     'news:detail', 
     'users:login', 
     'users:logout', 
     'users:signup',)
)
def test_pages_availability_for_anonymous_user(client, name, news):
    if name == 'news:detail':
        url = reverse(name, args=(news.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'param_client, expected_status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, comment_obj',  
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    )
)
def test_pages_availability_for_authorized_users(param_client, expected_status, name, comment_obj):
    url = reverse(name, args=(comment_obj.id,))
    response = param_client.get(url)
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    'name, comment_obj',  
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    )
)
def test_redirect_for_anonymous_user(client, name, comment_obj):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_obj.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
