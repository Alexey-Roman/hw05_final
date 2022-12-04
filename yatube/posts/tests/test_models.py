from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Bobi')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Обычный текст поста длиной будет 15',
        )

        cls.test_for_model = (
            (cls.post, cls.post.text[:Post.TEXT_LIMIT]),
            (cls.group, cls.group.title),
        )

    def test_models_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        for model, str_value in PostModelTest.test_for_model:
            with self.subTest(model=model):
                self.assertEqual(str(model), str_value)
