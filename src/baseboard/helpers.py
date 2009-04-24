"""Common functions shared across the baseboard project."""
import socket

from baseboard.models import Project

def update_summaries(debug, timeout=20):
    """Calls update_summary on all Project objects in the database."""
    problems = []
    errors = []
   
    old_timeout = socket.getdefaulttimeout() #Be kind
    socket.setdefaulttimeout(float(timeout))
    for proj in Project.objects.all():
        try:
            if debug == 2:
                print "Updating %s (%s)" % (proj.name, proj.id)
            proj.update_summary()
        except Exception, err:
            if debug == 2:
                print "ERROR updating %s (%s)" % (proj.name, proj.id)
            problems.append(err)
            errors.append("Error updating %s (%s): %s" % 
                    (proj, proj.id, str(err)))
    socket.setdefaulttimeout(old_timeout) #Rewind

    if errors and debug:
        print '\n'.join(errors)
        
    if problems:
        raise errors[0]

    return True
