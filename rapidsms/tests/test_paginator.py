from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from rapidsms.conf import settings
from rapidsms.templatetags.paginator_tags import paginator


class PaginatorTests(TestCase):
    def test_paginator(self):
        cases = [
            # viewing page, max_page, [shown pages] (None = ellipsis)
            (1, 10, [1, 2, 3, None, 9, 10]),
            (3, 10, [1, 2, 3, 4, 5, None, 9, 10]),
            (4, 10, [1, 2, 3, 4, 5, 6, None, 9, 10]),
            (10, 10, [1, 2, None, 8, 9, 10]),
            (6, 10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
            (5, 20, [1, 2, 3, 4, 5, 6, 7, None, 19, 20]),
            (18, 20, [1, 2, None, 16, 17, 18, 19, 20]),
            (17, 20, [1, 2, None, 15, 16, 17, 18, 19, 20]),
            (16, 20, [1, 2, None, 14, 15, 16, 17, 18, 19, 20]),
            (15, 20, [1, 2, None, 13, 14, 15, 16, 17, 18, 19, 20]),
            (20, 50, [1, 2, None, 18, 19, 20, 21, 22, None, 49, 50]),
        ]
        request = RequestFactory().get(
            reverse('rapidsms.contrib.registration.views.registration')
        )
        context = {'request': request}

        settings.PAGINATOR_BORDER_LINKS = 2
        settings.PAGINATOR_ADJACENT_LINKS = 2

        for page_num, max_num, test_case_pages in cases:
            pg = Paginator(range(max_num * 10), 10)
            result_pages = [
                p['number'] if p else None for p in
                paginator(context, pg.page(page_num))['page_links']
            ]
            self.assertEqual(result_pages, test_case_pages)
