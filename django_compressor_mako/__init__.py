#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mako.runtime import supports_caller
from django.test.utils import override_settings
from compressor.templatetags.compress import compress as compressor
from compressor.exceptions import OfflineGenerationError
from compressor.cache import (
    get_offline_hexdigest, write_offline_manifest, get_offline_manifest)


class NodeMock(object):
    def __init__(self, content, *args, **kwargs):
        self.content = content

    def render(self, *args, **kwargs):
        return self.content


class ParserMock(object):
    def __init__(self, body, *args, **kwargs):
        self.body = body

    def parse(self, *args, **kwargs):
        return NodeMock(self.body)

    def delete_first_token(self, *args, **kwargs):
        pass


class TokenMock(object):
    def __init__(self, *args, **kwargs):
        self.args = args

    def split_contents(self, *args, **kwargs):
        return self.args


@override_settings(COMPRESS_OFFLINE=False)
def offline_compress(parser, token, context):
    return compressor(parser, token).render(context)


def _compress(context, **kwargs):
    try:
        # Those arguments are mandatory to parse template fragment
        # and should be provided by mako
        capture = context['capture']
        caller = context['caller']
    except KeyError:
        return ''
    # print('||>>>', dict(context))

    parser = ParserMock(capture(caller.body))

    # `kind` is mandatory for django-compressor. but `kwargs.get` will return
    # None if not provided, so `django-compressor` can handle the error
    args = ['compress', kwargs.get('kind')]

    if 'mode' in kwargs:
        args.append(kwargs['mode'])

    if 'name' in kwargs:
        raise NotImplementedError('"name" is not supported')

    token = TokenMock(*args)

    try:
        return compressor(parser, token).render({})
    except OfflineGenerationError:
        # we prefer doing a try except rather than an if for performance issue
        key = get_offline_hexdigest(parser.body)
        offline_manifest = get_offline_manifest()
        if key not in offline_manifest:
            print('compressing:\n\n{}\n'.format(parser.body.strip()))
            compressed = offline_compress(parser, token, {})
            offline_manifest[key] = compressed
            write_offline_manifest(offline_manifest)
            print('compressed:\n\tkey: {}\n\thtml: {}\n'.format(
                key, compressed))


@supports_caller
def compress(context, **kwargs):
    return _compress(context, **kwargs)


@supports_caller
def css(context, **kwargs):
    kwargs['kind'] = 'css'
    return _compress(context, **kwargs)


@supports_caller
def js(context, **kwargs):
    kwargs['kind'] = 'js'
    return _compress(context, **kwargs)
