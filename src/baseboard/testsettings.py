DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/shorturls.db'
INSTALLED_APPS = ['baseboard']
ROOT_URLCONF = 'baseboard.urls'
BASEBOARD_CREDENTIALS = {
    'https://foo.basecamphq.com/': ('username1', 'password1'),
    'https://foo.updatelog.com/': ('username1', 'password1'),
    'http://foo.updatelog.com/': ('username1', 'password1'),
}
