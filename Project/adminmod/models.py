from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password

#Multiuser
#"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        GUARD = "GUARD", "Guard"

    base_role = Role.ADMIN

    role = models.CharField(max_length=50, choices=Role.choices, default='student')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)

class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.STUDENT)

class Student(User):

    base_role = User.Role.STUDENT

    student = StudentManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for students"

@receiver(post_save, sender=Student)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "STUDENT":
        StudentProfile.objects.create(user=instance)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(null=True, blank=True)

class GuardManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.GUARD)

class Guard(User):

    base_role = User.Role.GUARD

    guard = GuardManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for guards"

class GuardProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    guard_id = models.IntegerField(null=True, blank=True)

@receiver(post_save, sender=Guard)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "GUARD":
        GuardProfile.objects.create(user=instance)
#"""
#end mulitiuser

class DropdownOption(models.Model):
    program1 = models.CharField(max_length=255, default='Default Program')

    def __str__(self):
        return self.program1

class Course(models.Model):
    program = models.ForeignKey(DropdownOption, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)

    def __str__(self):
        return self.course_name


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=255)

    def __str__(self):
        return self.section_name

class Signup(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    middle_initial = models.CharField(max_length=1, null=True, blank=True, verbose_name='Middle Initial')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    idnumber = models.CharField(max_length=20, unique=True, verbose_name='ID Number')
    email = models.EmailField(unique=True, verbose_name='Email')
    password = models.CharField(max_length=8, verbose_name='Password')
    confirmpass = models.CharField(max_length=8, verbose_name='Confirm Password')
    program1 = models.ForeignKey(DropdownOption, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    id_picture = models.FileField(upload_to='id_pictures/', verbose_name='ID Picture')
    registration_cert = models.FileField(upload_to='registration_certs/', verbose_name='Certificate of Registration (COR)')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure that we are storing the plain-text password as entered
        # Don't use set_password or hash the password here
        super(Signup, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Violation Models
class ViolationType(models.Model):
    VIOLATION_TYPE_CHOICES = [
        ('Minor', 'Minor'),
        ('Major', 'Major'),
    ]
    name = models.CharField(max_length=255)
    violation_type = models.CharField(max_length=10, choices=VIOLATION_TYPE_CHOICES)
    description = models.TextField()
    guidelines = models.TextField()
    sanction = models.CharField(max_length=255, null=True, blank=True)  
    sanction_period_value = models.IntegerField()
    sanction_period_type = models.CharField(max_length=10, choices=[('Hours', 'Hours'), ('Day', 'Day'), ('Week', 'Week'), ('Month', 'Month')])

    def __str__(self):
        return self.name

class Report(models.Model):
    student = models.ForeignKey(Signup, on_delete=models.CASCADE)
    incident_date = models.DateField()
    violation_type = models.ForeignKey(ViolationType, on_delete=models.CASCADE)

    def __str__(self):
        return f"Report for {self.student.first_name} {self.student.last_name}"

class Userrole(models.Model):
    USER_CHOICES = [
        ('GUARD', 'GUARD'),
        ('INSTRUCTOR', 'INSTRUCTOR'),
        ('ADMIN', 'ADMIN')
    ]
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50, default='', null=True)
    middle_initial = models.CharField(max_length=1, blank=True, null=True, default='')
    last_name = models.CharField(max_length=50, default='', null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    position = models.CharField(max_length=10, choices=USER_CHOICES)
    
    def __str__(self):
        return f"{self.first_name} {self.middle_initial or ''} {self.last_name}".strip()

class ApprovedStudent(models.Model):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    middle_initial = models.CharField(max_length=1, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    idnumber = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    program1 = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    id_picture = models.FileField(upload_to='approved_id_pictures/', null=True, blank=True)
    registration_cert = models.FileField(upload_to='approved_registration_certs/', null=True, blank=True)
    approved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.idnumber})"


class RejectedStudent(models.Model):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    middle_initial = models.CharField(max_length=1, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    idnumber = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    program1 = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    id_picture = models.FileField(upload_to='rejected_id_pictures/', null=True, blank=True)
    registration_cert = models.FileField(upload_to='rejected_registration_certs/', null=True, blank=True)
    rejected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.idnumber})"