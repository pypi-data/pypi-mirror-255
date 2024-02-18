#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='Flask-uWSGI-Sockets',
    version='1.0',
    url='https://github.com/level09/flask_uwsgi_websocket',
    license='MIT',
    author='Nidal',
    author_email='level09@gmail.com',
    description='High-performance WebSockets for your Flask apps powered by uWSGI.',
    long_description=open('README.rst').read(),
    py_modules=['flask_uwsgi_websocket'],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    platforms='any',
    install_requires=[
        'Flask',
        'uwsgi',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='uwsgi flask websockets'
)
