import sys
import pprint

__previous_settings_module = ''
__overriden_settings = {}

def establish_settings():
    '''Sets up the Django settings (in lieu of DJANGO_SETTINGS_MODULE)'''
    defaults = dict(
        INSTALLED_APPS = ['baseboard', ],
        CACHE_BACKEND = "dummy://",
        DATABASE_ENGINE = "sqlite3",
        DATABASE_NAME = ":memory:",
        TEST_DATABASE_CHARSET = 'utf8',
        TEST_DATABASE_COLLATION = 'utf8_unicode_ci',
        ROOT_URLCONF = 'baseboard.urls',
        BASEBOARD_CREDENTIALS = {
            'https://foo.basecamphq.com/': ('username1', 'password1')
        },
    )

    import os
    __previous_settings_module = os.environ['DJANGO_SETTINGS_MODULE']
    os.environ['DJANGO_SETTINGS_MODULE'] = ''

    from django.conf import settings
    try:
        settings.configure(**defaults)
    except RuntimeError:
        for key, value in defaults.items():
            __overriden_settings[key] = value
            setattr(settings, key, value)

def restore_settings():
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] =  __previous_settings_module

    from django.conf import settings
    for key, value in __overriden_settings.items():
        setattr(settings, key, value)

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    '''Sets up the environment and runs tests for django-baseboard.'''
    establish_settings()

    from django.test.simple import run_tests
    failures = run_tests(test_labels, verbosity=verbosity, interactive=interactive, extra_tests=extra_tests)
    if failures:
        sys.exit(failures)

    restore_settings()

if __name__ == "__main__":
    run_tests(["baseboard"], 0)
