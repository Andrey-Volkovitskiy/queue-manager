from django.contrib.auth.models import User


def user_fullname_patch(self):
    return f"{self.first_name} {self.last_name}"


User.__str__ = user_fullname_patch


class Supervisor(User):
    class Meta:
        proxy = True
