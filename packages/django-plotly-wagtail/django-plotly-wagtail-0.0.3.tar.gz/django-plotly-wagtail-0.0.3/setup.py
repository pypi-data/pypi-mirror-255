#!/usr/bin/env python

from setuptools import setup


with open('dpwagtail/version.py') as f:
    exec(f.read())


with open('README.md') as f:
    long_description = f.read()


setup(
    name="django-plotly-wagtail",
    version=__version__,
    url="https://gitlab.com/GibbsConsulting/django-plotly-wagtail",
    description="Django Wagtail use of django-plotly-dash and plotly dash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gibbs Consulting",
    author_email="py.dpcms@gibbsconsulting.ca",
    license='AGPL v3',
    packages=[
        'dpwagtail',
        'dpwagtail.templatetags',
    ],
    include_package_data=True,
    classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Affero General Public License v3',
    'Programming Language :: Python :: 3',
    'Framework :: Dash',
    ],
    keywords='django plotly plotly-dash dash dashboard wagtail',
    project_urls = {
    'Source': "https://gitlab.com/GibbsConsulting/django-plotly-wagtail",
    'Tracker': "https://gitlab.com/GibbsConsulting/django-plotly-wagtail/issues",
    'Documentation': 'http://django-plotly-wagtail.readthedocs.io/',
    },
    install_requires = [
        'django>3.2',
        'django-plotly-dash',
        'wagtail',
    ],
    python_requires=">=3.9",
    )
