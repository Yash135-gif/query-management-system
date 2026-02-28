from django.db import models

class User(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.BigIntegerField(null=True, blank=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.role})"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.user.name} - {self.department.name if self.department else 'No Dept'}"


class UserQuery(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('pending_admin', 'Pending Admin'),
        ('closed', 'Closed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    assigned_employee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_queries"
    )

    forwarded_to_admin = models.BooleanField(default=False)

    
    title = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),
    ]

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )

    def __str__(self):
        return f"UserQuery #{self.id} - {self.user.name}"


 
class EmployeeQuery(models.Model):

    STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('pending_admin', 'Pending Admin'),
    ('closed', 'Closed'),
)

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    question = models.TextField()
    reply = models.TextField(null=True, blank=True)

    attachment = models.FileField(
        upload_to='employee_query_files/',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EmployeeQuery #{self.id} - {self.employee.name}"

class UserQueryMessage(models.Model):

    query = models.ForeignKey(
        UserQuery,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    attachment = models.FileField(
        upload_to='user_query_messages/',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message in Query #{self.query.id}"

class EmployeeQueryMessage(models.Model):

    query = models.ForeignKey(
        EmployeeQuery,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender_role=models.CharField(max_length=100,null=True)

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    attachment = models.FileField(
        upload_to='employee_query_messages/',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message in Employee Query #{self.query.id}"
    
