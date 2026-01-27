from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError

class Organization(models.Model):
    """Tenant model - represents a company/organization"""
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_client = models.BooleanField(default=False, help_text="Indicates if this organization is a client organization")
    
    def __str__(self):
        return self.name

class OrganizationRelationship(models.Model):
    """Tracks which organizations are clients of which organizations"""
    service_provider = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='client_relationships'
    )
    client = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='vendor_relationships'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['service_provider', 'client']
        verbose_name = 'Organization Relationship'
        verbose_name_plural = 'Organization Relationships'
    
    def __str__(self):
        return f"{self.client.name} is client of {self.service_provider.name}"

class Department(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='departments',
        limit_choices_to={'is_client': False}
    )
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'organization']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),  # Access all departments in their org
        ('department_head', 'Department Head'),  # Access all projects in their department
        ('employee', 'Employee'),  # Access assigned projects/tasks
        ('client', 'Client'),  # Access only client-visible tasks
    ]
    
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True,
        blank=True,
        limit_choices_to={'is_client': False}
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='employee')
    employee_id = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=False, null=False, default="")
    last_name = models.CharField(max_length=150, blank=False, null=False, default="")
    email = models.EmailField(blank=False, unique=True, null=False, default="")
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users',
    )
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Helper methods for permission checking
    def is_admin_role(self):
        return self.role == 'admin'
    
    def is_department_head_role(self):
        return self.role == 'department_head'
        
    def is_employee_role(self):
        return self.role == 'employee'
    
    def is_client_role(self):
        return self.role == 'client'
    
    def can_manage_users(self):
        """Can this user manage other users?"""
        return self.role in ['admin', 'department_head']
    
    def get_accessible_organizations(self):
        """Get the organization this user can access"""
        return Organization.objects.filter(id=self.organization.id)
    
    def get_accessible_departments(self):
        """Get all departments this user can access"""
        if self.is_admin_role():
            return self.organization.departments.all()
        elif self.is_department_head_role() and self.department:
            return Department.objects.filter(id=self.department.id)
        return Department.objects.none()
    
    def get_accessible_projects(self):
        """Get all projects this user can access"""
        if self.is_admin_role():
            return Project.objects.filter(organization=self.organization)
        elif self.is_department_head_role() and self.department:
            return Project.objects.filter(department=self.department)
        elif self.is_employee_role():
            return self.member_projects.all()
        elif self.is_client_role():
            return Project.objects.filter(client_organizations=self.organization)
        return Project.objects.none()
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.organization.name})"

    def clean(self):
        """Validate that department belongs to the user's organization"""
        super().clean()
        
        # Check if both organization and department are set
        if self.department and self.organization:
            # Verify department belongs to the organization
            if self.department.organization != self.organization:
                raise ValidationError({
                    'department': f'The department "{self.department.name}" does not belong to "{self.organization.name}". Please select a department from the same organization.'
                })
        
        # Optional: Validate role-specific requirements
        if self.role == 'department_head' and not self.department:
            raise ValidationError({
                'department': 'Department heads must be assigned to a department.'
            })
    
    def save(self, *args, **kwargs):
        """Always run validation before saving"""
        self.full_clean()  # This calls clean() method
        super().save(*args, **kwargs)
    
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='projects',
        limit_choices_to={'is_client': False}
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='projects'
    )
    project_lead = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='led_projects'
    )
    members = models.ManyToManyField(
        User, 
        related_name='member_projects', 
        blank=True
    )
    # Client organizations that have access to this project
    client_organizations = models.ManyToManyField(
        Organization,
        related_name='client_projects',
        blank=True,
        limit_choices_to={'is_client': True}
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    def save(self, *args, **kwargs):
        """Auto-add project lead to members when saved"""
        super().save(*args, **kwargs)
        if self.project_lead:
            self.members.add(self.project_lead)

class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ('feature', 'Feature'),
        ('bug', 'Bug'),
        ('documentation', 'Documentation'),
        ('testing', 'Testing'),
        ('research', 'Research'),
        ('support', 'Support Request'),  # New type for client-created tasks
        ('feedback', 'Client Feedback'),  # Another option for client input
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='owned_tasks',
        help_text="The organization that owns/manages this task",
        limit_choices_to={'is_client': False}
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='created_tasks',
        help_text="User who created this task"
    )
    
    # Client visibility and access control
    
    client_organizations = models.ManyToManyField(
        Organization,
        related_name='accessible_tasks',
        blank=True,
        limit_choices_to={'is_client': True},
        help_text="Client organizations that can view/edit this task"
    )
    client_can_edit = models.BooleanField(
        default=False,
        help_text="Whether client users can edit this task"
    )
    client_can_comment = models.BooleanField(
        default=True,
        help_text="Whether client users can comment on this task"
    )
    
    due_date = models.DateField(null=True, blank=True)
    parent_task = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subtasks'
    )
    dependency_tasks = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='dependent_tasks', 
        blank=True
    )
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'project']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.project.name})"
    
    def is_accessible_by_client(self, client_organization):
        """Check if a client organization can access this task"""
        return (
            self.client_organizations.filter(id=client_organization.id).exists()
        )
    
    def can_be_edited_by_client(self, client_organization):
        """Check if a client organization can edit this task"""
        return (
            self.client_can_edit and 
            self.is_accessible_by_client(client_organization)
        )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and self.assigned_to is None and self.project and self.project.project_lead:
            self.assigned_to = self.project.project_lead

        super().save(*args, **kwargs)

class TaskComment(models.Model):
    """Comments on tasks - useful for client communication"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal comments not visible to clients"
    )
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user} on {self.task.title}"

class TaskAttachment(models.Model):
    """File attachments for tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    file_link = models.FileField(upload_to='task_attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    is_client_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} on {self.task.title}"