from django.contrib import admin

from .models import Organization, Department, Project, User, Task, TaskComment, TaskAttachment
# Register your models here.

admin.site.register(Organization)
admin.site.register(Department)
admin.site.register(Project)
admin.site.register(User)
admin.site.register(Task)
admin.site.register(TaskComment)
admin.site.register(TaskAttachment)
