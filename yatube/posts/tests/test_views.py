import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.urls import reverse
from django.conf import settings

from ..models import Group, Post, Follow
from ..forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='VladimirMayakovsky')
        cls.follower = User.objects.create(username='Plato')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.group_no_post = Group.objects.create(
            title='Тестовая группы без поста',
            description='Описание для тестовой группы без поста',
            slug='slug-no-post'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_show_correct_context(self):
        """Проверка, что *.html шаблон выдаёт верный контекст в шаблон."""

        self.authorized_client.force_login(self.follower)
        Follow.objects.create(
            user=self.follower,
            author=self.user
        )
        templates_context = (
            (reverse('posts:index'), 'page_obj'),
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}), 'page_obj'),
            (reverse('posts:profile',
                     kwargs={'username': self.user.username}), 'page_obj'),
            (reverse('posts:post_detail',
                     kwargs={'post_id': self.post.id}), 'post'),
            (reverse('posts:follow_index'), 'page_obj'),

        )

        for url, objects in templates_context:
            response = self.authorized_client.get(url)
            if objects == 'page_obj':
                post_contex = response.context.get(objects).object_list[0]
            elif objects == 'post':
                post_contex = response.context['post']

            with self.subTest(post_contex=post_contex):
                self.assertEqual(post_contex.text, self.post.text)
                self.assertEqual(post_contex.author, self.post.author)
                self.assertEqual(post_contex.group.id, self.post.group.id)
                self.assertEqual(post_contex.image, self.post.image)

    def test_post_show_correct_context(self):
        """Проверка,
        что post_create и post_edit выдаёт верный контекст в шаблон.
        """

        templates_response = (
            (self.authorized_client.get(
                reverse('posts:create')), False),
            (self.authorized_client.get(
                reverse('posts:edit',
                        kwargs={'post_id': self.post.id})), True),
        )
        for response, check in templates_response:
            self.assertIn('is_edit', response.context)
            self.assertIs(response.context['is_edit'], check)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], PostForm)
            if check:
                self.assertEqual(
                    response.context.get('form').instance, self.post
                )

    def test_post_put_in_render_user_and_group(self):
        """Проверка, что user и group выдаёт верный контекст в шаблон.
        """

        templates_context = (
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}),
             'group', self.group),
            (reverse('posts:profile',
                     kwargs={'username': self.user.username}),
             'author', self.user),
        )

        for url, objects, postfrom in templates_context:
            response = self.authorized_client.get(url)
            self.assertEqual(response.context[objects], postfrom)

    def test_post_after_create_not_in_another_group(self):
        """Проверка, что пост не попадает в чужую группу."""

        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group_no_post.slug,)))
        self.assertNotEqual(response.context['group'], self.group)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_cache_index_page(self):
        """Тестирование кэша"""
        post = Post.objects.create(
            text='Пост для теста кэша',
            author=self.user)
        content_add = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_add, content_cache_clear)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Daniel')
        cls.follower = User.objects.create(username='Plato')

        cls.post = Post.objects.create(
            text='Подпишись на меня',
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_follow_on_user(self):
        """Подписка на других пользователей"""

        self.author_client.force_login(self.follower)
        self.author_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author})
        )
        follow = Follow.objects.last()
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.author_id, self.author.id)
        self.assertEqual(follow.user_id, self.follower.id)

    def test_unfollow_on_user(self):
        """Проверка отписки от пользователя."""

        self.author_client.force_login(self.follower)
        Follow.objects.create(
            user=self.follower,
            author=self.author,
        )
        self.author_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author})
        )
        self.assertEqual(Follow.objects.count(), 0)
        self.assertFalse(Follow.objects.filter(
            user=self.follower,
            author=self.author,).exists()
        )

    def test_notfollow_on_authors(self):
        """Проверка записей у тех кто не подписан."""

        post = Post.objects.create(
            author=self.author,
            text="Подпишись на меня")
        response = self.author_client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
