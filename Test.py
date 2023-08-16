from user.tasks import print_text_task
from user.tasks import print_purchase_count_task
from celery.result import AsyncResult
from user.models import User, Purchase
import time
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User


#task 1


def test_print_text_task():
    text = "Testing Celery task"
    result = print_text_task.delay(text)

    timeout = 5
    start_time = time.time()
    while not result.ready():
        if time.time() - start_time > timeout:
            assert False, "Task took too long to complete"
        time.sleep(0.1)

    assert result.successful(), "Task was not successful"


def test_print_purchase_count_task():
    user = User.objects.create(username="testuser")
    Purchase.objects.create(user=user, item="item1")
    Purchase.objects.create(user=user, item="item2")

    user_id = user.id
    result = print_purchase_count_task.delay(user_id)

    timeout = 5
    start_time = time.time()
    while not result.ready():
        if time.time() - start_time > timeout:
            assert False, "Task took too long to complete"
        time.sleep(0.1)

    assert result.successful(), "Task was not successful"


#task 2


class UserModelTest(TestCase):

    def test_create_user(self):
        """
        Тестує створення об'єкта User.
        """
        username = "testuser"
        email = "test@example.com"
        password = "testpassword"
        user = User.objects.create_user(username=username, email=email, password=password)

        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)


#task 3


User = get_user_model()

class UserViewSetTest(APITestCase):

    def test_create_user(self):
        """
        Тестує створення об'єкта User через API.
        """
        url = '/users/'
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_access_user(self):
        """
        Тестує доступ до об'єкта User через API.
        """
        user = User.objects.create(username='testuser', email='test@example.com', password='testpassword')
        url = f'/users/{user.id}/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_delete_user(self):
        """
        Тестує видалення об'єкта User через API.
        """
        user = User.objects.create(username='testuser', email='test@example.com', password='testpassword')
        url = f'/users/{user.id}/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)