from django.contrib.auth import get_user_model

from ..drf.metadata import DRFFieldDict

User = get_user_model()


class TagFieldDict(DRFFieldDict):
    widgets = {
        'type': 'hidden',
        'category': 'hidden',
        'order': 'hidden',
    }


class UserFieldDict(DRFFieldDict):
    widgets = {
        'password': 'hidden',
    }

