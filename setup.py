import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-baseboard",
    version = "0.3",
    url = 'http://github.com/cmheisel/django-baseboard',
    license = 'MIT',
    description = "Dashboard view across various Basecamp projects, powered by Django",
    long_description = read('README'),
    
    author = 'Chris Heisel',
    author_email = 'chris@heisel.org',
    
    packages = find_packages('src'),
    package_dir = {'': 'src'},

    install_requires = ['setuptools', 'basecampreporting', 'feedparser'],

    
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

