#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages


setup(
    name='django4-2-datatable',
    packages = ['table'],
    version='0.3.2',
    author='shymonk',
    author_email='hellojohn201@gmail.com',
    url='https://github.com/kamilanindita/django42-datatable',
    description='A simple Django app to origanize data in tabular form.',
    long_description=open('README.rst').read(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["django>=4.2"],
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ],
)
