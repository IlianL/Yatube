import shutil
import tempfile
from http import HTTPStatus
import time

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Follow


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()

ONE_POST: int = 1
POSTS_IN_FIRST_PAGE_MAX: int = 10
POSTS_IN_SECOND_PAGE: int = 5
POSTS_IN_SECOND_PAGE_GROUP: int = 4
POSTS_IN_SECOND_PAGE_AUTH: int = 4


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_2 = User.objects.create_user(username='auth_2')
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user_2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа c одним постом',
            slug='test_group_2',
            description='Тестовое описание, тут один пост',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_14 = SimpleUploadedFile(
            name='small_14.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.uploaded_15 = SimpleUploadedFile(
            name='small_15.gif',
            content=small_gif,
            content_type='image/gif'
        )

        for i in range(1, 16):
            if i not in (14, 15):
                Post.objects.create(
                    author=cls.user,
                    text=f'№ {i} Тест пост',
                    group=cls.group
                )
                time.sleep(0.01)
            elif i == 14:
                Post.objects.create(
                    author=cls.user,
                    text=f'№ {i} Тест пост',
                    group=cls.group,
                    image=cls.uploaded_14
                )
                time.sleep(0.01)
            else:
                Post.objects.create(
                    author=cls.user_2,
                    text=f'№ {i} Тест пост',
                    group=cls.group_2,
                    image=cls.uploaded_15
                )

        cls.post = Post.objects.get(id=1)
        cls.post_14 = Post.objects.get(id=14)
        cls.post_15 = Post.objects.get(id=15)

        cls.INDEX_URL = reverse('posts:index')
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list', args=[cls.group.slug]
        )
        cls.GROUP_LIST_2_URL = reverse(
            'posts:group_list', args=[cls.group_2.slug]
        )
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user.username])
        cls.PROFILE_2_URL = reverse('posts:profile',
                                    args=[cls.user_2.username])
        cls.POST_DETAIL_URL = reverse('posts:post_detail',
                                      args=[cls.post_15.id])
        cls.POST_COMMENT_URL = reverse('posts:add_comment',
                                       args=[cls.post_15.id])
        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_namespase_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            self.INDEX_URL: 'posts/index.html',
            self.POST_CREATE_URL: 'posts/create_or_update_post.html',
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_EDIT_URL: 'posts/create_or_update_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pagintator_correct_posts_num(self):
        """Пагинатор показывает правильное количество постов."""
        page_2 = '?page=2'
        paginator_two_pages = {
            self.INDEX_URL: POSTS_IN_FIRST_PAGE_MAX,
            self.INDEX_URL + page_2: POSTS_IN_SECOND_PAGE,
            self.GROUP_LIST_URL: POSTS_IN_FIRST_PAGE_MAX,
            self.GROUP_LIST_URL + page_2: POSTS_IN_SECOND_PAGE_GROUP,
            self.GROUP_LIST_2_URL: ONE_POST,
            self.PROFILE_URL: POSTS_IN_FIRST_PAGE_MAX,
            self.PROFILE_URL + page_2: POSTS_IN_SECOND_PAGE_AUTH,
            self.PROFILE_2_URL: ONE_POST
        }
        for reverse_name, posts_num in paginator_two_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                paginator = response.context['page_obj']
                self.assertEqual(len(paginator.object_list), posts_num)

    def test_correct_context(self):
        """
        Шаблоны index  group_list profile
        сформированы с правильным контекстом.
        """
        content_post_15 = [self.post_15.text, self.post_15.author.username,
                           self.post_15.group.title, self.post_15.image]
        content_post_14 = [self.post_14.text, self.post_14.author.username,
                           self.post_14.group.title, self.post_14.image]
        context_expected = {
            self.INDEX_URL: content_post_15,
            self.GROUP_LIST_URL: content_post_14,
            self.PROFILE_URL: content_post_14,
            self.PROFILE_2_URL: content_post_15,
            self.GROUP_LIST_2_URL: content_post_15
        }
        for reverse_name, expected in context_expected.items():
            response = self.authorized_client.get(reverse_name)
            first_object = response.context['page_obj'][0]
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(first_object.text, expected[0])
                self.assertEqual(first_object.author.username, expected[1])
                self.assertEqual(first_object.group.title, expected[2])
                self.assertEqual(first_object.image, expected[3])

    def test_post_detail_show_correct_context(self):
        """Один пост по id с правильным контекстом."""
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        post = response.context.get('post')
        context_check = {
            post.text: self.post_15.text,
            post.author.username: self.post_15.author.username,
            post.group.title: self.post_15.group.title,
            post.pk: self.post_15.pk,
            post.image: self.post_15.image
        }
        for field, expected_result in context_check.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_result)

    def test_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_EDIT_URL)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def unauthorized_user_permission(self):
        """Провека дотупа неавторизованного пользователя."""
        url_status_client = {
            self.POST_CREATE_URL: HTTPStatus.FOUND,
            self.POST_EDIT_URL: HTTPStatus.FOUND,
            self.POST_COMMENT_URL: HTTPStatus.FOUND
        }
        for address, status in url_status_client.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=self.user,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='post_author'
        )
        cls.post_follower = User.objects.create_user(
            username='post_follower'
        )
        cls.post = Post.objects.create(
            text='Лайк подписка если кодишь',
            author=cls.post_author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.post_author)
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.post_follower)

        cls.FOLLOW_AUTH = reverse(
            'posts:profile_follow', args=[cls.post_author]
        )
        cls.UNFOLLOW_AUTH = reverse(
            'posts:profile_unfollow', args=[cls.post_author]
        )
        cls.FOLLOW_POSTS_LIST = reverse('posts:follow_index')

    def test_user_can_follow(self):
        """Проверка подписки на автора."""
        count_follow = Follow.objects.count()
        self.follower_client.get(self.FOLLOW_AUTH)
        follow_obj = Follow.objects.get(id=1)
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow_obj.author.id, self.post_author.id)
        self.assertEqual(follow_obj.user.id, self.post_follower.id)

    def test_user_can_unfollow(self):
        """Пользователь может отписаться."""
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_author
        )
        count_follow = Follow.objects.count()
        self.follower_client.get(self.UNFOLLOW_AUTH)
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_follow_post(self):
        """Проверка записей у тех кто подписан."""
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_author
        )
        response = self.follower_client.get(self.FOLLOW_POSTS_LIST)
        self.assertIn(self.post, response.context['page_obj'].object_list)

    def test_not_follow_post(self):
        """Проверка записей у тех кто не подписан."""
        response = self.follower_client.get(self.FOLLOW_POSTS_LIST)
        self.assertNotIn(self.post, response.context['page_obj'].object_list)
