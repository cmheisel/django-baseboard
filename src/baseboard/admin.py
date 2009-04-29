from urllib2 import HTTPError

from django.contrib import admin
from django import forms

from baseboard.models import Project, Dashboard, RSSFeed

class DashboardAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}
    filter_horizontal = ('projects', )
    list_display = ('name', 'description', '_project_count')
    search_fields = ('name', 'description')

    def _project_count(self, dash):
        return dash.projects.count()
    _project_count.short_description = "Project count"
    
admin.site.register(Dashboard, DashboardAdmin)

class ProjectAdminForm(forms.ModelForm):
    def clean_basecamp_url(self):
        url = self.cleaned_data['basecamp_url']

        basecamp_id = Project.extract_basecamp_id(url)
        api_url = Project.extract_basecamp_api_url(url)
        if not basecamp_id or not api_url:
            raise forms.ValidationError("%s does not appear to be a valid basecamp url" % url)

        credentials = Project.get_credentials_for(api_url)
        if not credentials:
            raise forms.ValidationError("No credentials for %s" % api_url)

        username, password = credentials

        p = Project.BasecampProject(api_url, basecamp_id, username, password)
        try:
            p.name
        except HTTPError, e:
            raise forms.ValidationError("Error connecting to Basecamp. Does user %s have access to the project?" % username)
        return url

class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    date_hierarchy = 'created_at'
    list_display=('name', 'updated_at', 'basecamp_updated_at', '_dashboard_count')
    list_filter=('updated_at', 'basecamp_updated_at')
    filter_horizontal=('feeds', )
    search_fields=('name', 'description')
    fieldsets = (
        (None, {
            'fields': ("basecamp_url", "basecamp_id", "description", "name", "slug", "feeds"),
        }),
        ('Advanced options', {
            'classes': ('collapse', ),
            'fields': ('readable_summary', 'update_error'),
        }),
    )
    
    def _dashboard_count(self, proj):
        return proj.dashboards.count()
    _dashboard_count.short_description = "Dashboard count"
    
admin.site.register(Project, ProjectAdmin)

class FeedAdmin(admin.ModelAdmin):
    list_display=('name', 'url')
    search_fields = ('name', 'url')
    
admin.site.register(RSSFeed, FeedAdmin)

