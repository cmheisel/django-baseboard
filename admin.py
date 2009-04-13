from django.contrib import admin
from django import forms

from baseboard.models import Project, Dashboard

class DashboardAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}
    filter_horizontal = ('projects', )
    list_display = ('name', 'description', '_project_count')

    def _project_count(self, dash):
        return dash.projects.count()
    _project_count.short_description = "Project count"
    
admin.site.register(Dashboard, DashboardAdmin)

class ProjectAdminForm(forms.ModelForm):
    def clean_basecamp_url(self):
        url = self.cleaned_data['basecamp_url']

        try:
            Project.verify_basecamp_url(url)
        except KeyError:
            protocol, domain = url.split('/')[0], url.split('/')[2]
            
            raise forms.ValidationError("Your setup does not include access to projects on %s//%s" % protocol, domain)

class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    date_hierarchy = 'created_at'
    list_display=('name', 'updated_at', 'basecamp_updated_at', '_dashboard_count')
    list_filter=('updated_at', 'basecamp_updated_at')
    fieldsets = (
        (None, {
            'fields': ("basecamp_url", "description", "name", "slug"),
        }),
        ('Advanced options', {
            'classes': ('collapse', ),
            'fields': ('basecamp_id', 'readable_summary'),
        }),
    )
    
    def _dashboard_count(self, proj):
        return proj.dashboards.count()
    _dashboard_count.short_description = "Dashboard count"
    
admin.site.register(Project, ProjectAdmin)
