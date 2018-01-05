from __future__ import unicode_literals
import os
import sys

from fnmatch import fnmatch
from importlib import import_module

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings as dj_settings
from django.utils import six
from django.utils.encoding import smart_text
from django.template.loader import get_template  # noqa Leave this in to preload template locations
from django.template import engines

from compressor.cache import write_offline_manifest, get_offline_manifest
from compressor.conf import settings
from compressor.exceptions import (OfflineGenerationError, TemplateSyntaxError,
                                   TemplateDoesNotExist)
from compressor.utils import get_mod_func

if six.PY3:
    # there is an 'io' module in python 2.6+, but io.StringIO does not
    # accept regular strings, just unicode objects
    from io import StringIO
else:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO


def error_handler(*args, **kwargs):
    '''Bypass all errors during compression'''
    # Critical error like FileNotFoundError will still be raised
    # but database connection error or TypeError will be catched
    return True


class Command(BaseCommand):
    help = "Compress content outside of the request/response cycle"

    def add_arguments(self, parser):
        parser.add_argument(
            '--extension', '-e', action='append', dest='extensions',
            help='The file extension(s) to examine (default: ".mako", '
                 'separate multiple extensions with commas, or use -e '
                 'multiple times)')
        parser.add_argument(
            '-f', '--force', default=False, action='store_true',
            help="Force the generation of compressed content even if the "
                 "COMPRESS_ENABLED setting is not True.", dest='force')

    def get_loaders(self):
        return [
            e.engine.lookup
            for e in engines.all() if e.__class__.__name__ == 'MakoBackend']

    def __get_parser(self):
        engine = [
            e for e in engines.all() if e.__class__.__name__ == 'MakoBackend'
        ][0]

        # hijack template options to set custom error handler
        for ts in dj_settings.TEMPLATES:
            if 'mako' in ts['BACKEND']:
                ts['APP_DIRS'] = ts.get('APP_DIRS', False)
                ts.pop('BACKEND')
                ts['OPTIONS']['error_handler'] = error_handler
                engine.__init__(ts)
        return engine

    def compress(self, log=None, **options):
        """
        Searches templates containing 'compress' nodes and compresses them
        "offline" -- outside of the request/response cycle.

        The result is cached with a cache-key derived from the content of the
        compress nodes (not the content of the possibly linked files!).
        """
        extensions = options.get('extensions')
        extensions = self.handle_extensions(extensions or ['mako'])
        verbosity = int(options.get("verbosity", 0))
        if not log:
            log = StringIO()
        if not self.get_loaders():
            raise OfflineGenerationError("No template loaders defined. You "
                                         "must set TEMPLATE_LOADERS in your "
                                         "settings or set 'loaders' in your "
                                         "TEMPLATES dictionary.")
        templates = set()
        for path in self.get_loaders()[0].directories:
            for root, dirs, files in os.walk(
                    path, followlinks=options.get('followlinks', False)):
                templates.update(
                    os.path.join(root, name)[len(path):]
                    for name in files if not name.startswith('.') and any(
                        fnmatch(name, "*%s" % glob) for glob in extensions))

        if not templates:
            raise OfflineGenerationError("No templates found. Make sure your "
                                         "TEMPLATE_LOADERS and TEMPLATE_DIRS "
                                         "settings are correct.")
        if verbosity > 1:
            log.write("Found templates:\n\t" + "\n\t".join(templates) + "\n")

        contexts = settings.COMPRESS_OFFLINE_CONTEXT
        if isinstance(contexts, six.string_types):
            try:
                module, function = get_mod_func(contexts)
                contexts = getattr(import_module(module), function)()
            except (AttributeError, ImportError, TypeError) as e:
                raise ImportError(
                    "Couldn't import offline context function %s: %s" % (
                        settings.COMPRESS_OFFLINE_CONTEXT, e))
        elif not isinstance(contexts, (list, tuple)):
            contexts = [contexts]
        contexts = list(contexts)  # evaluate generator

        parser = self.__get_parser()
        for template_name in templates:
            try:
                template = parser.get_template(template_name)
            except IOError:  # unreadable file -> ignore
                if verbosity > 0:
                    log.write("Unreadable template at: %s\n" % template_name)
                continue
            except TemplateSyntaxError as e:  # broken template -> ignore
                if verbosity > 0:
                    log.write("Invalid template %s: %s\n" % (
                        template_name, smart_text(e)))
                continue
            except TemplateDoesNotExist:  # non existent template -> ignore
                if verbosity > 0:
                    log.write("Non-existent template at: %s\n" % template_name)
                continue
            except UnicodeDecodeError:
                if verbosity > 0:
                    log.write("UnicodeDecodeError while trying to read "
                              "template %s\n" % template_name)
                continue

            for context_dict in contexts:
                try:
                    from django.test.client import RequestFactory
                    request = RequestFactory().get('/')
                    context_dict['request'] = request
                    # mako compress tag will compress and upadate manifest
                    template.render(context=context_dict, request=request)
                except (TemplateDoesNotExist, TemplateSyntaxError) as e:
                    # Could be an error in some base template
                    if verbosity > 0:
                        log.write("Error parsing template %s: %s\n" %
                                  (template_name, smart_text(e)))
                    continue

    def handle_extensions(self, extensions=('html',)):
        """
        organizes multiple extensions that are separated with commas or
        passed by using --extension/-e multiple times.

        for example: running 'django-admin compress -e js,txt -e xhtml -a'
        would result in an extension list: ['.js', '.txt', '.xhtml']

        >>> handle_extensions(['.html', 'html,js,py,py,py,.py', 'py,.py'])
        ['.html', '.js']
        >>> handle_extensions(['.html, txt,.tpl'])
        ['.html', '.tpl', '.txt']
        """
        ext_list = []
        for ext in extensions:
            ext_list.extend(ext.replace(' ', '').split(','))
        for i, ext in enumerate(ext_list):
            if not ext.startswith('.'):
                ext_list[i] = '.%s' % ext_list[i]
        return set(ext_list)

    def handle(self, **options):
        if not settings.COMPRESS_ENABLED and not options.get("force"):
            raise CommandError(
                "Compressor is disabled. Set the COMPRESS_ENABLED "
                "setting or use --force to override.")
        if not settings.COMPRESS_OFFLINE:
            if not options.get("force"):
                raise CommandError(
                    "Offline compression is disabled. Set "
                    "COMPRESS_OFFLINE or use the --force to override.")

        options.setdefault("log", sys.stdout)

        manifest = {}
        engines = [e.strip() for e in options.get("engines", [])] or ["mako"]
        for engine in engines:
            opts = options.copy()
            opts["engine"] = engine
            self.compress(**opts)
            manifest.update(get_offline_manifest())
        write_offline_manifest(manifest)


Command.requires_system_checks = False
