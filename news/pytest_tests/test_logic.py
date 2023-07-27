import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING,BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_create_comment(reader_client, reader, news, form_data):
    url = reverse('news:detail', args=(news.id,))    
    response = reader_client.post(url, data=form_data)
    success_url = reverse('news:detail', kwargs={'pk': news.id}) + '#comments'
    assertRedirects(response, success_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.author == reader
    assert new_comment.text == form_data['text']

def test_danger_comments(reader_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    for word in BAD_WORDS:
        data = form_data
        data.update({'text': form_data['text'] + ' ' + word })
        response = reader_client.post(url, data=data)
        assertFormError(response, 'form', 'text', errors=(WARNING))
        assert Comment.objects.count() == 0 

def test_author_can_edit_comment(author_client, author, form_data, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    success_url = reverse('news:detail', kwargs={'pk': comment.news.pk}) + '#comments'
    assertRedirects(response, success_url)
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.author == author
    assert new_comment.text == form_data['text']

def test_other_user_cant_edit_comment(reader_client, author, form_data, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.text == comment.text

def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    success_url = reverse('news:detail', kwargs={'pk': comment.news.pk}) + '#comments'
    assertRedirects(response, success_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1 