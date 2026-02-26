from django.contrib import admin

from .models import Project, Task, TaskComment


class TenantAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "tenant", "role")
    search_fields = ("username", "email")
    list_filter = ("tenant", "role")


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "tenant")
    search_fields = ("name",)
    list_filter = ("tenant",)


class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project", "tenant")
    search_fields = ("name",)
    list_filter = ("tenant", "project")


class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "author", "task", "tenant", "created_at")
    search_fields = ("content",)
    list_filter = ("tenant", "author", "task")


# admin.site.register(Tenant, TenantAdmin)
# admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskComment, TaskCommentAdmin)
