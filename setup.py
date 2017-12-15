from setuptools import setup
import codecs


def long_description():
    with codecs.open('README.rst', encoding='utf-8') as f:
        return f.read()


setup(
    name='django_compressor_mako',
    version='0.0.5',
    description='Mako template support for django_compressor',
    long_description=long_description(),
    url='http://github.com/orus-io/django-compressor-mako',
    author='Steeve Chailloux',
    author_email='steeve.chailloux@orus.io',
    license='MIT',
    packages=['django_compressor_mako'],
    classifiers=[
        'Development Status :: 4 - Beta',
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
