import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, Comment
from posts.forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест пост',
            group=cls.group
        )
        cls.form = PostForm()
        cls.INDEX_URL = reverse('posts:index')
        cls.GROUP_LIST_URL = reverse(
            'posts:group_list', args=[cls.group.slug]
        )
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user.username])
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_COMMENT_URL = reverse('posts:add_comment', args=[cls.post.id])
        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает пост."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст да',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            self.POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.PROFILE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = response.context['page_obj'][0]

        self.assertTrue(
            Post.objects.filter(
                id=post.id,
                text=post.text,
                group=post.group.id,
                author=post.author,
                image=post.image.name
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует пост, редирект."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_change.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Redacted post',
            'group': self.post.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True,
        )
        post = response.context['post']
        check_post = {
            post.text: form_data['text'],
            post.group.id: form_data['group'],
            post.author: self.post.author,
            post.image: 'posts/small_change.gif'
        }
        for post, expected in check_post.items():
            with self.subTest(post=post):
                self.assertEqual(post, expected)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_comments(self):
        """Коммментарии добавляются, текст соответствует."""
        comment_count = self.post.comments.count()
        form_data = {
            'text': 'Тестовый коммент'
        }
        response = self.authorized_client.post(
            self.POST_COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(self.post.comments.get(id=1).text, form_data['text'])
