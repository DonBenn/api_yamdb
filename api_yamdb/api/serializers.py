from rest_framework import serializers

from reviews.constants import (
    EMAIL_LENGTH,
    MAX_TITLE_SCORE,
    MIN_TITLE_SCORE,
)
from reviews.models import Category, Comments, Genre, Review, Title, User
from reviews.validators import validate_username


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Класс сериализатора для произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Настройки сериализатора модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    score = serializers.IntegerField(
        min_value=MIN_TITLE_SCORE, max_value=MAX_TITLE_SCORE
    )
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """Метаданные сериализатора отзывов."""

        fields = '__all__'
        model = Review

    def validate(self, data):
        """Метод валидации данных добавления отзыва."""
        author = self.context['request'].user
        title_id = self.context['view'].kwargs['title_id']

        if self.context['request'].method == 'POST':
            if author.reviews.filter(title=title_id):
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )

        return data


class CommentsSerializer(serializers.ModelSerializer):
    """Настройки сериализатора модели Comment."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """Метаданные сериализатора комментариев."""

        fields = '__all__'
        model = Comments


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[validate_username],
        required=True,
        max_length=150,
    )
    email = serializers.EmailField(required=True, max_length=EMAIL_LENGTH)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(email=email, username=username).exists():
            return data
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': 'Username already taken'}
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Email already registered'}
            )
        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        user, _ = User.objects.get_or_create(email=email, username=username)
        return user


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
