from csv import reader
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api_yamdb.settings import BASE_DIR
from reviews.models import (
    Category, Comments, Genre, Review, Title, TitleGenres
)


User = get_user_model()


def load_categories(row):
    Category.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2]
    )


def load_genres(row):
    Genre.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2]
    )


def load_titles(row):
    Title.objects.get_or_create(
        id=row[0],
        name=row[1],
        year=row[2],
        category_id=row[3]
    )


def load_genre_titles(row):
    TitleGenres.objects.get_or_create(
        id=row[0],
        title_id=row[1],
        genre_id=row[2]
    )


def load_reviews(row):
    title = Title.objects.get(id=row[1])
    author = User.objects.get(id=row[3])
    Review.objects.get_or_create(
        id=row[0],
        title=title,
        text=row[2],
        author=author,
        score=row[4],
        pub_date=row[5]
    )


def load_comments(row):
    review = Review.objects.get(id=row[1])
    author = User.objects.get(id=row[3])
    Comments.objects.get_or_create(
        id=row[0],
        review=review,
        text=row[2],
        author=author,
        pub_date=row[4]
    )


def load_users(row):
    User.objects.get_or_create(
        id=row[0],
        username=row[1],
        email=row[2],
        role=row[3],
        bio=row[4],
        first_name=row[5],
        last_name=row[6]
    )


files_functions = (
    ('category.csv', load_categories),
    ('genre.csv', load_genres),
    ('titles.csv', load_titles),
    ('genre_title.csv', load_genre_titles),
    ('users.csv', load_users),
    ('review.csv', load_reviews),
    ('comments.csv', load_comments)
)


class Command(BaseCommand):
    help = 'Начало загрузки файлов'

    def handle(self, *args, **options):
        for file, function in files_functions:
            file_path = os.path.join(BASE_DIR, "static/data", file)
            with open(file_path, 'r', encoding='utf-8') as current_file:
                content = reader(current_file)
                next(content)
                for row in content:
                    function(row)
            self.stdout.write(f'{file} загружен!')
        self.stdout.write('Загрузка завершена')
