from django.contrib import admin

from credentials.apps.catalog.models import Course, CourseRun, Organization, Pathway, Program
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from threading import Thread
import time
from django.core.management import call_command

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "uuid", "title")
    list_filter = ("site",)
    readonly_fields = ("id", "key", "uuid", "title", "owners", "site")
    search_fields = ("id", "key", "title", "uuid")
    # Manprax
    def has_add_permission(self, request):
        return False


@admin.register(CourseRun)
class CourseRunAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "uuid", "title_override", "start_date", "end_date")
    readonly_fields = ("id", "key", "uuid", "title_override", "start_date", "end_date", "course")
    search_fields = ("id", "key", "title_override", "uuid", "course__title")
    # Manprax
    def has_add_permission(self, request):
        return False

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "uuid", "type")
    list_filter = ("site",)
    readonly_fields = (
        "title",
        "uuid",
        "type",
        "course_runs",
        "site",
        "authoring_organizations",
        "type_slug",
        "total_hours_of_effort",
        "status",
    )
    search_fields = ("title", "uuid")

    # Manprax 
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'sync-catalog/',
                self.admin_site.admin_view(self.sync_catalog_view),
                name='admin_sync_catalog',
            ),
        ]
        return custom_urls + urls

    def sync_catalog_view(self, request):
        def run_sync():
            try:
                call_command("copy_catalog", verbosity=0)
                print("copy_catalog completed successfully")  # in docker logs
            except Exception as e:
                print(f"copy_catalog failed: {str(e)}")

        Thread(target=run_sync, daemon=True).start()
        time.sleep(1.5)

        messages.info(
            request,
            "Catalog sync (copy_catalog) started in background. "
            "Check logs: tutor local logs credentials -f"
        )

        return HttpResponseRedirect('../')
    
    def has_add_permission(self, request):
        return False

@admin.register(Pathway)
class PathwayAdmin(admin.ModelAdmin):
    list_display = ("name", "org_name", "pathway_type", "email", "uuid")
    list_filter = ("site",)
    readonly_fields = ("name", "org_name", "pathway_type", "email", "uuid", "site", "programs")
    search_fields = ("name", "uuid")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "uuid")
    list_filter = ("site",)
    readonly_fields = ("name", "key", "uuid", "site", "certificate_logo_image_url")
    search_fields = ("name", "key", "uuid")
    # Manprax
    def has_add_permission(self, request):
        return False
