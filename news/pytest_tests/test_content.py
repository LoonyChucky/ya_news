import pytest

from django.urls import reverse
from django.conf import settings

from ..models import News

@pytest.mark.django_db
@pytest.mark.usefixtures('bulk_news')
def test_news_items_in_list(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_on_page = len(object_list)
    assert news_on_page <= settings.NEWS_COUNT_ON_HOME_PAGE

@pytest.mark.django_db
@pytest.mark.usefixtures('bulk_news')
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates

@pytest.mark.usefixtures('bulk_comments', 'news')
def test_comments_order(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news_on_page = response.context['news']
    all_comments = news_on_page.comment_set.all()
    com_dates = [comment.created for comment in all_comments]
    sort_dates = sorted(com_dates)
    assert com_dates == sort_dates

@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context

def test_authorized_client_has_form(reader_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = reader_client.get(url)
    assert 'form' in response.context
