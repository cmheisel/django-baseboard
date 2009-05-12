"""Common functions shared across the baseboard project."""
import socket

from baseboard.models import Project, RSSFeed

def run_instance_update_method(queryset, method_name, debug, timeout=20):
    """Loops through every object in queryset, and calls method_name.
    If debug is true, it prints error messages to stdout
    Optional timeout value is used to keep long-running network operations from stalling
    the entire process.
    """

    exceptions = []
    error_msgs = []
   
    old_timeout = socket.getdefaulttimeout() #Be kind
    socket.setdefaulttimeout(float(timeout))
    for obj in queryset:
        method = getattr(obj, method_name)
        try:
            if debug == 2:
                print "Updating %s" % (obj, )
            method()
            if hasattr(obj, 'update_error'):
                obj.update_error = ''
                obj.save()
        except Exception, err:
            if hasattr(obj, 'update_error'):
                obj.update_error = str(err)
                obj.save()

            msg = "ERROR updating %s => %s" % (obj, str(err))
            if debug == 2:
                print msg
            exceptions.append(err)
            error_msgs.append(msg)

    socket.setdefaulttimeout(old_timeout) #Rewind

    if error_msgs and debug:
        print '\n'.join(error_msgs)
        
    if exceptions:
        return False

    return True

def update_summaries(debug, timeout=20):
    """Calls update_summary on all Project objects in the database."""
    return run_instance_update_method(Project.objects.all(), 'update_summary', debug, timeout)

def update_feeds(debug, timeout=20):
    """Calls update_feed on all RSSFeed objects in the database."""
    return run_instance_update_method(RSSFeed.objects.all(), 'update_feed', debug, timeout)
