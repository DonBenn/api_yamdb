from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """Проверка на администраторские доступы."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_staff
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    """Проверка на администраторский доступ, иначе - только чтение."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorOrReadOnly(BasePermission):
    """Класс в котором проверяется пользователь.

    Проверяется является ли пользователь владельцем объекта,
    разрещая ему редактировать его.
    """

    def has_permission(self, request, view):
        """Метод проверяет аутефецикацию и безопасный метод."""
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Метод проверяет является ли user автором, модератором или админом.

        Безопасный ли метод запроса
        """
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
