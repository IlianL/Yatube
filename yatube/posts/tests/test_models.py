from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_correct_models_str(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_post_text = self.post.text[:15] + '...'
        expected_group_text = self.group.title
        models_obj = {
            self.post: expected_post_text,
            self.group: expected_group_text
        }
        for model_instance, expected_text in models_obj.items():
            with self.subTest(model_instance=model_instance):
                self.assertEqual(expected_text, str(model_instance))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        field_verboses_post = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Название группы',
        }
        field_verboses_group = {
            'title': 'Название группы',
            'description': 'Описание группы',
        }
        # Это не слишком кхм.. странная конструкция?
        for dict in [field_verboses_post, field_verboses_group]:
            for field, expected_value in dict.items():
                with self.subTest(field=field):
                    if dict == field_verboses_post:
                        self.assertEqual(
                            post._meta.get_field(field).verbose_name,
                            expected_value)
                    else:
                        self.assertEqual(
                            group._meta.get_field(field).verbose_name,
                            expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group
        field_help_post = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        field_help_group = {
            'title': 'Название вашей груупы будет видно всем пользователям',
            'description': 'Чему будет посвящена ваша группа?',
        }

        for dict in [field_help_post, field_help_group]:
            for field, expected_value in dict.items():
                with self.subTest(field=field):
                    if dict == field_help_post:
                        self.assertEqual(
                            post._meta.get_field(field).help_text,
                            expected_value)
                    else:
                        self.assertEqual(
                            group._meta.get_field(field).help_text,
                            expected_value)
