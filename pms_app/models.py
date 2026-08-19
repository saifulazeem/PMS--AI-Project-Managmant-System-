from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ─────────────────────────────────────────────
# Custom User Manager
# ─────────────────────────────────────────────

class UserManager(BaseUserManager):
    def create_user(self, email, u_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, u_name=u_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, u_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        return self.create_user(email, u_name, password, **extra_fields)


# ─────────────────────────────────────────────
# User
# ─────────────────────────────────────────────

class User(AbstractBaseUser, PermissionsMixin):
    """
    Central user entity. Maps to the 'User' table in the ERD.
    """
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Supervisor"),
        ("member", "Lead"),
    ]

    id        = models.AutoField(primary_key=True)
    u_name      = models.CharField(max_length=150)
    email       = models.EmailField(unique=True)
    role        = models.CharField(max_length=50, choices=ROLE_CHOICES, default="Lead")
    is_active   = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    is_deleted  = models.BooleanField(default=False)

    # Required by AbstractBaseUser
    is_staff    = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["u_name"]

    class Meta:
        db_table = "users"
        verbose_name = "User"

    def __str__(self):
        return f"{self.u_name} <{self.email}>"

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    @property
    def id(self):
        return self.id


# ─────────────────────────────────────────────
# Team Members
# ─────────────────────────────────────────────

class TeamMember(models.Model):
    """
    Represents a team member profile. Maps to 'Team_Members' in the ERD.
    The 'added_by' FK references User (who added this team member).
    """
    id         = models.AutoField(primary_key=True)
    name          = models.CharField(max_length=150)
    desc          = models.TextField(blank=True, null=True)
    skills        = models.CharField(max_length=255, blank=True, null=True)
    role          = models.CharField(max_length=100, blank=True, null=True)
    added_by      = models.ForeignKey(
                        User,
                        on_delete=models.SET_NULL,
                        null=True,
                        related_name="added_team_members",
                        db_column="added_by"
                    )
    qualitifcation = models.CharField(max_length=255, blank=True, null=True)
    experience    = models.IntegerField(default=0)
    updated_at    = models.DateTimeField(auto_now=True)
    is_deleted    = models.IntegerField(default=0)   # ERD specifies int

    class Meta:
        db_table = "team_members"
        verbose_name = "Team Member"

    def __str__(self):
        return self.name

# ─────────────────────────────────────────────
# Projects
# ─────────────────────────────────────────────

class Project(models.Model):
    """
    Core project entity. Maps to 'Projects' in the ERD.
    """
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("active", "Active"),
        ("on_hold", "On Hold"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    p_id       = models.AutoField(primary_key=True)
    p_name     = models.CharField(max_length=255)
    desc       = models.TextField(blank=True, null=True)
    priority   = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default="medium")
    created_by = models.ForeignKey(
                     User,
                     on_delete=models.SET_NULL,
                     null=True,
                     related_name="created_projects",
                     db_column="created_by"
                 )
    deadline   = models.DateTimeField(null=True, blank=True)
    status     = models.CharField(max_length=50, choices=STATUS_CHOICES, default="planning")
    created_at = models.DateTimeField(auto_now_add=True)
    start_at   = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "projects"
        verbose_name = "Project"

    def __str__(self):
        return self.p_name

    def soft_delete(self):
        self.is_deleted = True
        self.save()

# ─────────────────────────────────────────────
# Tasks
# ─────────────────────────────────────────────

class Task(models.Model):
    """
    Task entity. Maps to 'Tasks' in the ERD.
    assign_to / assign_by / created_by all reference User.
    p_id references Project.
    """
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("review", "In Review"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ]

    t_id       = models.AutoField(primary_key=True)
    title      = models.CharField(max_length=255)
    desc       = models.TextField(blank=True, null=True)
    status     = models.CharField(max_length=50, choices=STATUS_CHOICES, default="todo")
    assign_to  = models.ForeignKey(
                     TeamMember,
                     on_delete=models.SET_NULL,
                     null=True,
                     blank=True,
                     related_name="assigned_tasks",
                     db_column="assign_to"
                 )
    assign_by  = models.ForeignKey(
                     User,
                     on_delete=models.SET_NULL,
                     null=True,
                     blank=True,
                     related_name="tasks_assigned_by_me",
                     db_column="assign_by"
                 )
    created_by = models.ForeignKey(
                     User,
                     on_delete=models.SET_NULL,
                     null=True,
                     blank=True,
                     related_name="created_tasks",
                     db_column="created_by"
                 )
    created_at  = models.DateTimeField(auto_now_add=True)
    p           = models.ForeignKey(
                      Project,
                      on_delete=models.CASCADE,
                      related_name="tasks",
                      db_column="p_id"
                  )
    priority    = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default="medium")
    due_date    = models.DateTimeField(null=True, blank=True)
    start_date  = models.DateTimeField(null=True, blank=True)
    update_last = models.DateTimeField(auto_now=True)
    is_deleted  = models.BooleanField(default=False)

    class Meta:
        db_table = "tasks"
        verbose_name = "Task"

    def __str__(self):
        return self.title

    def soft_delete(self):
        self.is_deleted = True
        self.save()

