from baseboard.models import Project

def update_summaries(debug):
    """Calls update_summary on all Project objects in the database."""
    problems = []
    errors = []
    
    for p in Project.objects.all():
        #try:
        p.update_summary()
        #except Exception, e:
            #problems.append(e)
            #errors.append("Error updating %s (%s): %s" % (p, p.id, str(e)))

    if errors and debug:
        print '\n'.join(errors)
        
    if problems:
        raise errors[0]

    return True
