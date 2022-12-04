from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='super_author',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='testing_slug',
            description='Тестовое описание группы',
        )

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)

    def test_authorized_user_create_post(self):
        """Проверка создания записи авторизированным клиентом."""
        Post.objects.all().delete()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        self.assertEqual(Post.objects.count(), 1)
        db_post = Post.objects.last()
        self.assertEqual(db_post.text, form_data['text'])
        self.assertEqual(db_post.author, self.post_author)
        self.assertEqual(db_post.group_id, form_data['group'])

    def test_authorized_user_edit_post(self):
        """Проверка редактирования записи авторизированным клиентом."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
        )

        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse(
                'posts:edit',
                args=[post.id]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        db_post = Post.objects.get(id=post.id)
        self.assertEqual(db_post.author, post.author)
        self.assertEqual(db_post.text, form_data['text'])
        self.assertEqual(db_post.group_id, form_data['group'])

    def test_nonauthorized_user_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста для редактирования',
            'group': self.group.id,
        }

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text=form_data['text']).exists())
