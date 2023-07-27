import pytest
from datetime import timedelta, datetime
from time import sleep
from django.conf import settings
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')

@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client

@pytest.fixture
def reader(django_user_model):  
    return django_user_model.objects.create(username='Читатель')

@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client

@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news

@pytest.fixture(scope='function')
def bulk_news():
    now = timezone.now()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
            news = News(title=f'Новость {index}',
                        text='Просто текст.',
                        date=now - timedelta(days=index))
            all_news.append(news)
    News.objects.bulk_create(all_news)

@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст новости',
    )
    return comment

@pytest.fixture(scope='function')
def bulk_comments(author, news):
    now = datetime.today()
    comments = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment(news=news,
                          author=author,
                          text=f'Просто текст{index}.', 
                          created=now,
                        )
        now += timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
