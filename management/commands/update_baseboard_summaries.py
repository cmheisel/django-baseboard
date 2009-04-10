from optparse import make_option

from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
    )

    help = "Updates all django-baseboard.Project instances from Basecamp."

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 1))
        
        from baseboard.helpers import update_summaries
        update_summaries(verbosity)
