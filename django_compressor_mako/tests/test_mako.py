# -*- coding: utf-8 -*-
from __future__ import with_statement, unicode_literals

from django.test import TestCase
from django.test.utils import override_settings
from mako.exceptions import CompileException

from compressor.conf import settings
from compressor.tests.test_base import css_tag


class TestMakoCompressor(TestCase):

    def setUp(self):
        from mako.template import Template
        self.template = Template

    def wrap(self, body, tag):
        return ''.join([
            '<%namespace name="compress" module="django_compressor_mako"/>',
            '<%compress:' + tag + '>',
            body,
            '</%compress:' + 'compress>'
            if 'kind' in tag else '</%compress:' + tag + '>',
        ])

    @override_settings(COMPRESS_ENABLED=False)
    def test_compress_is_disabled(self):
        tag_body = '\n'.join([
            '<link rel="stylesheet" href="css/one.css" '
            'type="text/css" charset="utf-8">',
            '<style type="text/css">p { border:5px solid green;}</style>',
            '<link rel="stylesheet" href="css/two.css" '
            'type="text/css" charset="utf-8">',
        ])
        template_string = self.wrap(tag_body, 'compress kind="css"')
        template = self.template(template_string)
        self.assertEqual(tag_body, template.render())

    # unfortunatly mako doesn't allow blocks inside of <%call>
    def test_empty_tag(self):
        template = self.wrap('<%block name="js"/>', 'compress kind="js"')
        self.assertRaises(CompileException, self.template, template)

    def test_css_tag(self):
        template = self.template(self.wrap(''.join([
            '<link rel="stylesheet" href="${ STATIC_URL }css/one.css" '
            'type="text/css" charset="utf-8">',
            '<style type="text/css">p { border:5px solid green;}</style>',
            '<link rel="stylesheet" href="${ STATIC_URL }css/two.css" '
            'type="text/css" charset="utf-8">',
            ]), 'compress kind="css"'))
        context = {'STATIC_URL': settings.COMPRESS_URL}
        out = css_tag("/static/CACHE/css/58a8c0714e59.css")
        self.assertEqual(out, template.render(**context))

    def test_nonascii_css_tag(self):
        template = self.template(self.wrap(''.join([
            '<link rel="stylesheet" href="${ STATIC_URL }css/nonasc.css" '
            'type="text/css" charset="utf-8">',
            '<style type="text/css">p { border:5px solid green;}</style>',
            ]), 'css'))
        context = {'STATIC_URL': settings.COMPRESS_URL}
        out = css_tag("/static/CACHE/css/4263023f49d6.css")
        self.assertEqual(out, template.render(**context))

    def test_js_tag(self):
        template = self.template(self.wrap(''.join([
            '<script src="${ STATIC_URL }js/one.js" '
            'type="text/javascript" charset="utf-8"></script>',
            '<script type="text/javascript" '
            'charset="utf-8">obj.value = "value";</script>',
            ]), 'compress kind="js"'))
        context = {'STATIC_URL': settings.COMPRESS_URL}
        out = '<script type="text/javascript" ' \
            'src="/static/CACHE/js/74e158ccb432.js"></script>'
        self.assertEqual(out, template.render(**context))

    def test_nonascii_js_tag(self):
        template = self.template(self.wrap(''.join([
            '<script src="${ STATIC_URL }js/nonasc.js" '
            'type="text/javascript" charset="utf-8"></script>',
            '<script type="text/javascript" '
            'charset="utf-8">var test_value = "\u2014";</script>',
            ]), 'compress kind="js"'))
        context = {'STATIC_URL': settings.COMPRESS_URL}
        out = '<script type="text/javascript" ' \
            'src="/static/CACHE/js/a18195c6ae48.js"></script>'
        self.assertEqual(out, template.render(**context))

    def test_nonascii_latin1_js_tag(self):
        template = self.template(self.wrap(''.join([
            '<script src="${ STATIC_URL }js/nonasc-latin1.js" '
            'type="text/javascript" charset="latin-1"></script>',
            '<script type="text/javascript">'
            'var test_value = "\u2014";</script>',
            ]), 'js'))
        context = {'STATIC_URL': settings.COMPRESS_URL}
        out = '<script type="text/javascript" ' \
            'src="/static/CACHE/js/f64debbd8878.js"></script>'
        self.assertEqual(out, template.render(**context))

    def test_css_inline(self):
        template = self.template(self.wrap(''.join([
            '<link rel="stylesheet" href="${ STATIC_URL }css/one.css" '
            'type="text/css" charset="utf-8">',
            '<style type="text/css">p { border:5px solid green;}</style>',
            ]), 'compress kind="css" mode="inline"'))
        context = {'STATIC_URL': settings.COMPRESS_URL}
        out = '\n'.join([
            '<style type="text/css">body { background:#990; }',
            'p { border:5px solid green;}</style>',
        ])
        self.assertEqual(out, template.render(**context))

    def test_js_inline(self):
        template = self.template(self.wrap(''.join([
            '<script src="${ STATIC_URL }js/one.js" type="text/css" '
            'type="text/javascript" charset="utf-8"></script>',
            '<script type="text/javascript" charset="utf-8">'
            'obj.value = "value";</script>',
            ]), 'compress kind="js" mode="inline"'))
        context = {'STATIC_URL': settings.COMPRESS_URL}
        out = '<script type="text/javascript">' \
            ';obj={};;obj.value="value";</script>'
        self.assertEqual(out, template.render(**context))

    def test_named_css(self):
        template = self.template(self.wrap(''.join([
            '<link rel="stylesheet" href="${ STATIC_URL }css/one.css" '
            'type="text/css" charset="utf-8">',
            '<style type="text/css">p { border:5px solid green;}</style>',
            '<link rel="stylesheet" href="${ STATIC_URL }css/two.css" '
            'type="text/css" charset="utf-8">',
            ]), 'compress kind="css" mode="file" name="cute"'))
        context = {'STATIC_URL': settings.COMPRESS_URL}
        self.assertRaises(NotImplementedError, template.render, **context)
