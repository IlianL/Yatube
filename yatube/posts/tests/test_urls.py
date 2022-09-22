from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client

from posts.models import Post, Group

from http import HTTPStatus

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_2 = User.objects.create_user(username='not_auth')
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.user_2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.INDEX_URL = '/'
        cls.GROUP_LIST_URL = f'/group/{cls.group.slug}/'
        cls.PROFILE_URL = f'/profile/{cls.user.username}/'
        cls.POST_DETAIL_URL = f'/posts/{cls.post.id}/'
        cls.POST_COMMENT_URL = f'/posts/{cls.post.id}/comment/'
        cls.POST_CREATE_URL = '/create/'
        cls.POST_EDIT_URL = f'/posts/{cls.post.id}/edit/'
        cls.CHECK_404_URL = '/test_404_page/'
    
    def setUp(self):
        cache.clear()

    def test_url_at_desired_location(self):
        """
        Проверка страниц на доступ авторизованному и неавторизованному
        пользователю, статус страниц, редиректы.
        """
        allowed_to_all = [
            self.INDEX_URL, self.GROUP_LIST_URL, self.PROFILE_URL,
            self.POST_DETAIL_URL
        ]
        allowed_to_authorized_user = [
            self.POST_CREATE_URL
        ]
        allowed_to_author_only = [self.POST_EDIT_URL]
        unexisting_page = self.CHECK_404_URL

        url_status_client = {
            self.INDEX_URL: StaticURLTests.guest_client,
            self.GROUP_LIST_URL: StaticURLTests.guest_client,
            self.PROFILE_URL: StaticURLTests.guest_client,
            self.POST_DETAIL_URL: StaticURLTests.guest_client,
            unexisting_page: StaticURLTests.guest_client,
            self.POST_CREATE_URL: [
                StaticURLTests.guest_client,
                StaticURLTests.authorized_client
            ],
            self.POST_EDIT_URL: [
                StaticURLTests.guest_client,
                StaticURLTests.authorized_client,
                StaticURLTests.authorized_client_not_author
            ],
        }
        for address, client in url_status_client.items():
            with self.subTest(address=address):
                if address in allowed_to_all:
                    response = client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif address in allowed_to_authorized_user:
                    response = client[0].get(address)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                    response_user = client[1].get(address)
                    self.assertEqual(response_user.status_code, HTTPStatus.OK)
                elif address in allowed_to_author_only:
                    response = client[0].get(address)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.FOUND)
                    response_user_author = client[1].get(address)
                    self.assertEqual(
                        response_user_author.status_code, HTTPStatus.OK
                    )
                    user_not_author = client[2].get(address)
                    self.assertEqual(
                        user_not_author.status_code, HTTPStatus.FOUND
                    )
                elif address in unexisting_page:
                    response = client.get(address)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    raise ValueError(
                        f'Неизвестный адрес {address}')

    def test_urls_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.INDEX_URL: 'posts/index.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.POST_CREATE_URL: 'posts/create_or_update_post.html',
            self.POST_EDIT_URL: 'posts/create_or_update_post.html',

        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
