from django.db.models import QuerySet, Q

from user.models import User


class UserService:
    @classmethod
    def find_users(cls, pattern: str) -> QuerySet[User]:
        return User.objects.filter(
            Q(username__contains=pattern) | Q(first_name__contains=pattern) | Q(last_name__contains=pattern)
        )
