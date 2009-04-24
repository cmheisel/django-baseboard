"""Common functions shared across the baseboard project."""

from baseboard.models import Project

def update_summaries(debug):
    """Calls update_summary on all Project objects in the database."""
    problems = []
    errors = []
    
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

    if errors and debug:
        print '\n'.join(errors)
        
    if problems:
        raise errors[0]

    return True
