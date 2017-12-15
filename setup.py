from setuptools import setup
import os
import codecs


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as f:
        return f.read()


setup(
    name='django_compressor_mako',
    version='0.0.1',
    description='Mako template support for django_compressor',
    long_description=read('README.rst'),
    url='http://github.com/orus-io/django-compressor-mako',
    author='Steeve Chailloux',
    author_email='steeve.chailloux@orus.io',
    license='MIT',
    packages=['django_compressor_mako'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ],
    zip_safe=False)
