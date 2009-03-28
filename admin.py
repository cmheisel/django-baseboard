from django.contrib import admin

from baseboard.models import Project, Dashboard

class DashboardAdmin(admin.ModelAdmin): pass
admin.site.register(Dashboard, DashboardAdmin)

class ProjectAdmin(admin.ModelAdmin): pass
admin.site.register(Project, ProjectAdmin)
