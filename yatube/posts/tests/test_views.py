from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='VladimirMayakovsky')
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
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_show_correct_context(self):
        """Проверка, что *.html шаблон выдаёт верный контекст в шаблон."""

        templates_context = (
            (reverse('posts:index'), 'page_obj'),
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}), 'page_obj'),
            (reverse('posts:profile',
                     kwargs={'username': self.user.username}), 'page_obj'),
            (reverse('posts:post_detail',
                     kwargs={'post_id': self.post.id}), 'post'),
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
