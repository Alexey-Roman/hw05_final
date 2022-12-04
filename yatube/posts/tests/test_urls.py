from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class UrlAbsPathTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_post = User.objects.create(username='Daniel')
        cls.user_no_post = User.objects.create(username='Plato')

        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )

        cls.post = Post.objects.create(
            text='Обычный текст',
            author=cls.user_post,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user_post)

    def test_check_asolute_path_200(self):
        """Проверка StatusCode для гостевым и авторизованным пользователей."""

        url_user_status = [
            (reverse('posts:index'),
             self.client, HTTPStatus.OK),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             self.client, HTTPStatus.OK),
            (reverse('posts:profile', kwargs={'username': self.user_post}),
             self.client, HTTPStatus.OK),
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             self.client, HTTPStatus.OK),
            (reverse('posts:edit', kwargs={'post_id': self.post.id}),
             self.authorized_author, HTTPStatus.OK),
            (reverse('posts:create'),
             self.authorized_author, HTTPStatus.OK),
            ('/unexisting_page/',
             self.client, HTTPStatus.NOT_FOUND),
        ]
        for url, user, status in url_user_status:
            with self.subTest(url=url):
                status_code = user.get(url).status_code
                self.assertEqual(status_code, status)

    def test_url_redirect_anonymous_on_other_url(self):
        """Страница по адресу /create/ и /posts/<int:post_id>/edit/
         перенаправит анонимного пользователя на страницу.
        """

        url_target = [
            (reverse('posts:create'),
             f"{reverse('users:login')}?next={reverse('posts:create')}"),
            (reverse('posts:edit', kwargs={'post_id': self.post.id}),
             (f"{reverse('users:login')}?next="
             f"{reverse('posts:edit', kwargs={'post_id': self.post.id})}")
             )
        ]
        for url, target in url_target:
            response = self.guest_client.get(url, follow=True)
            self.assertRedirects(response, target)

    def test_edit_url_redirect_user_no_auth_on_post(self):
        """Страница по адресу /posts/<int:post_id>/edit/ перенаправит
         не автора поста на страницу поста.
        """

        self.authorized_author.force_login(self.user_no_post)
        response = self.authorized_author.get(
            reverse('posts:edit', kwargs={'post_id': self.post.id}),
            follow=True)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = [
            (reverse('posts:index'),
             'posts/index.html'),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             'posts/group_list.html'),
            (reverse('posts:profile', kwargs={'username': self.user_post}),
             'posts/profile.html'),
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             'posts/post_detail.html'),
            (reverse('posts:edit', kwargs={'post_id': self.post.id}),
             'posts/create_post.html'),
            (reverse('posts:create'),
             'posts/create_post.html'),
        ]
        for address, template in templates_url_names:
            with self.subTest(adress=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_name_reverse(self):
        """Проверка правильности url через reverse(name)"""

        name_url = [
            (reverse(
                'posts:index'), '/',),
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}),
             f'/group/{self.group.slug}/'),
            (reverse(
                'posts:profile',
                kwargs={'username': self.user_post}),
             f'/profile/{self.user_post}/'),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}),
             f'/posts/{self.post.id}/'),
            (reverse(
                'posts:edit',
                kwargs={'post_id': self.post.id}),
             f'/posts/{self.post.id}/edit/'),
            (reverse(
                'posts:create'), '/create/'),
        ]

        for name, url in name_url:
            with self.subTest(name=name, url=url):
                self.assertEqual(url, name)

    def test_url_404_get_custom_pages(self):
        """Проверка, что страница 404 отдаёт кастомный шаблон"""
        response = self.client.get('/defunct/page/')
        self.assertTemplateUsed(response, 'core/404.html')
