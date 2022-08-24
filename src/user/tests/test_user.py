import pytest
import factory

from rest_framework.test import APIClient

from .factory import UserFactory


@pytest.mark.django_db
@pytest.mark.parametrize('pattern, result', [('user', 3), ('3', 1), ('U', 0), ('t', 0)])
def test_find_user(pattern, result):
    user_1 = UserFactory(username='user_1')
    UserFactory(username='user_2')
    UserFactory(username='user_3')
    client = APIClient()
    client.force_authenticate(user=user_1)
    
    response = client.get('/api/user/users/find-user/', data={'pattern': pattern}, format='json')
    assert len(response.data.get('results')) == result
