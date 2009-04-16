from setuptools import setup, find_packages

setup(
    name = "django-baseboard",
    version = "0.1",
    url = 'http://github.com/cmheisel/django-baseboard',
    license = 'MIT',
    description = "Dashboards that display summaries from Basecamp projects.",
    author = 'Chris Heisel',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools', 'basecampreporting'],
)

