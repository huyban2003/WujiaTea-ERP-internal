"""Test Knowledge portal — cụm C4 (WJ-KNW-001…004). Chạy: `--test-tags wujia_knowledge`.

  1. `TestKnowledgeVisibility` — field text strip HTML + domain hiển thị (publish date
     tương lai / hết hạn / draft / archived / inactive).
  2. `TestKnowledgePortal` — controller: filter rác không lộ thông tin, thông báo khi bài
     đã gỡ, search theo summary/content, giờ portal đúng Asia/Ho_Chi_Minh.
"""

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase

from odoo.addons.wujia_portal_base.controllers.utils import fmt_local_dt
from odoo.addons.wujia_portal_knowledge.controllers.portal import _visible_domain


class KnowledgeCommon:

    @classmethod
    def _setup_knowledge(cls):
        cls.category = cls.env['wujia.knowledge.category'].create({
            'name': 'C4 Category', 'sequence': 1})
        cls.now = fields.Datetime.now()
        cls.article = cls.env['wujia.knowledge.article'].create({
            'name': 'Checklist mở cửa hàng buổi sáng',
            'slug': 'c4-checklist-mo-cua-hang',
            'category_id': cls.category.id,
            'summary': 'Tóm tắt cho bài Checklist mở cửa hàng buổi sáng.',
            # Keyword bị thẻ HTML cắt ngang → chỉ bản strip mới khớp.
            'content': '<p>Nội dung <strong>chi tiết</strong> cho bài viết.</p>',
            'state': 'published',
            'publish_date': cls.now - timedelta(days=1),
        })

    @classmethod
    def _article(cls, name, slug, **vals):
        return cls.env['wujia.knowledge.article'].create(dict({
            'name': name, 'slug': slug, 'category_id': cls.category.id,
            'state': 'published', 'publish_date': cls.now - timedelta(days=1),
        }, **vals))


@tagged('post_install', '-at_install', 'wujia_knowledge')
class TestKnowledgeVisibility(KnowledgeCommon, TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_knowledge()

    def test_content_text_strips_markup(self):
        self.assertEqual(
            self.article.wujia_content_text, 'Nội dung chi tiết cho bài viết.')

    def test_content_text_follows_content(self):
        self.article.content = '<div>Quy trình <em>đóng</em> ca tối</div>'
        self.assertEqual(self.article.wujia_content_text, 'Quy trình đóng ca tối')

    def test_visible_domain_excludes_hidden_articles(self):
        hidden = {
            'draft': self._article('Draft', 'c4-draft', state='draft'),
            'archived': self._article('Archived', 'c4-arch', state='archived'),
            'inactive': self._article('Inactive', 'c4-inactive', active=False),
            'expired': self._article(
                'Expired', 'c4-expired', expired_date=self.now - timedelta(hours=1)),
            'future': self._article(
                'Future', 'c4-future', publish_date=self.now + timedelta(days=3)),
        }
        visible = self.env['wujia.knowledge.article'].search(_visible_domain())
        self.assertIn(self.article, visible)
        for label, rec in hidden.items():
            self.assertNotIn(rec, visible, 'Bài %s không được hiện trên portal' % label)

    def test_fmt_local_dt_shifts_to_portal_tz(self):
        """UTC 09:05 phải in ra 16:05 giờ Asia/Ho_Chi_Minh (WJ-KNW-002)."""
        self.assertEqual(
            fmt_local_dt(datetime(2026, 8, 12, 9, 5), '%d/%m/%Y %H:%M'),
            '12/08/2026 16:05')


@tagged('post_install', '-at_install', 'wujia_knowledge')
class TestKnowledgePortal(KnowledgeCommon, HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_knowledge()
        cls.env['res.users'].create({
            'name': 'knw_user', 'login': 'knw_user', 'password': 'knw_user',
            'group_ids': [(6, 0, [cls.env.ref('base.group_portal').id])],
        })

    def setUp(self):
        super().setUp()
        self.authenticate('knw_user', 'knw_user')

    def _get(self, url):
        return self.url_open(url, timeout=30)

    def _assert_no_leak(self, res):
        self.assertEqual(res.status_code, 200)
        for leak in ('wujia.knowledge.category', 'wujia.knowledge.tag',
                     'User: ', 'Traceback'):
            self.assertNotIn(leak, res.text)

    def test_unknown_category_shows_friendly_notice(self):
        res = self._get('/portal/knowledge?category_id=999999')
        self._assert_no_leak(res)
        self.assertIn('Danh mục đã chọn không còn khả dụng.', res.text)

    def test_unknown_tag_shows_friendly_notice(self):
        res = self._get('/portal/knowledge?tag_id=999999')
        self._assert_no_leak(res)
        self.assertIn('Thẻ đã chọn không còn khả dụng.', res.text)

    def test_inactive_category_shows_friendly_notice(self):
        cat = self.env['wujia.knowledge.category'].create(
            {'name': 'C4 Inactive cat', 'active': False})
        res = self._get('/portal/knowledge?category_id=%s' % cat.id)
        self._assert_no_leak(res)
        self.assertIn('Danh mục đã chọn không còn khả dụng.', res.text)

    def test_valid_category_still_filters(self):
        res = self._get('/portal/knowledge?category_id=%s' % self.category.id)
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.article.name, res.text)
        self.assertNotIn('không còn khả dụng', res.text)

    def test_unpublished_slug_shows_notice(self):
        gone = self._article('Đã gỡ', 'c4-da-go')
        gone.state = 'draft'
        res = self._get('/portal/knowledge/c4-da-go')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Bài viết không tồn tại hoặc không còn khả dụng.', res.text)
        self.assertNotIn('Đã gỡ', res.text)

    def test_attachment_of_unpublished_article_redirects(self):
        gone = self._article('Đã gỡ 2', 'c4-da-go-2')
        gone.state = 'draft'
        res = self._get('/portal/knowledge/c4-da-go-2/attachment/1')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Bài viết không tồn tại hoặc không còn khả dụng.', res.text)

    def test_search_matches_summary(self):
        res = self._get('/portal/knowledge?keyword=Tóm+tắt+cho+bài+Checklist')
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.article.name, res.text)

    def test_search_matches_content_across_markup(self):
        res = self._get('/portal/knowledge?keyword=Nội+dung+chi+tiết')
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.article.name, res.text)

    def test_search_without_match_shows_empty_state(self):
        res = self._get('/portal/knowledge?keyword=zzz-khong-co-gi')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Chưa có bài viết', res.text)

    def test_detail_prints_local_time(self):
        self.article.publish_date = datetime(2026, 8, 12, 9, 5)
        res = self._get('/portal/knowledge/%s' % self.article.slug)
        self.assertEqual(res.status_code, 200)
        self.assertIn('12/08/2026 16:05', res.text)
