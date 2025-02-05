# Django core imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import (HttpResponse,HttpResponseRedirect,get_object_or_404,redirect,render,)
from django.utils import timezone
from django.conf import settings
from .models import (Course,DropdownOption,Report,Section,Signup,User,ViolationType,Userrole, ApprovedStudent, RejectedStudent)
from django.db import transaction, IntegrityError
# Local imports
from .forms import (ReportForm,SignupNow,UserroleForm,ViolationTypeForm,)

# Python standard library imports
import datetime, random, string
# ------ Admin Dashboard ------
def dashboard(request):
    return render(request,'Dashboard.html')

def DenyReport(request):
    return render(request, 'DenyReport.html')

# ------ User Roles ------
def userrole(request):
    return render(request, 'Account List.html') 

def edituserrole(request):
    return render(request, 'Edit User Role.html')

def generate_random_password():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

def useraccount(request):
    return render(request, 'UserAccount.html')

def adduser(request):
    if request.method == 'POST':
        form = UserroleForm(request.POST)
        if form.is_valid():
            # Extract form data
            employee_id = form.cleaned_data['employee_id']
            first_name = form.cleaned_data['first_name']
            middle_initial = form.cleaned_data['middle_initial']
            last_name = form.cleaned_data['last_name']
            position = form.cleaned_data['position']
            
            # Generate email based on first and last name
            email = f"{last_name.lower()}.{first_name.lower()}@email.com"
            password = generate_random_password()
            
            # Create the user in the database
            userrole = Userrole.objects.create(
                employee_id=employee_id,
                first_name=first_name,
                middle_initial=middle_initial,
                last_name=last_name,
                email=email,
                password=password,
                position=position,
            )

            # Pass generated email and password to the template
            return render(request, 'Add User.html', {
                'form': UserroleForm(),  # Clear the form after submission
                'success_message': "User was successfully created."  # Add success message
            })
        else:
            return render(request, 'Add User.html', {'form': form})

    # Generate a random password for the initial GET request
    password = generate_random_password()
    return render(request, 'Add User.html', {
        'form': UserroleForm(),
        'generated_password': password
    })

# View for generating a new password via AJAX
def retry_password(request):
    if request.method == 'GET':
        new_password = generate_random_password()
        return JsonResponse({'generated_password': new_password})

def useraccount(request):
    return render(request, 'user_role/UserAccount.html')
#------ Login ------

def login(request):
    return render(request, 'login/LOGIN.html')

def login_view(request):
    if request.method == 'POST':
        idnumber = request.POST.get('id-number')
        password = request.POST.get('password')
        
        try:
            user = Signup.objects.get(idnumber=idnumber)
            if password == user.password:  # Compare with plain text password
                # Log in user (store user ID and course ID in session, for example)
                request.session['user_id'] = user.id
                request.session['course_id'] = user.course.id  # Only store course ID, not the full object
                return redirect('studentstatus')  # Redirect to landing page
            else:
                error = "Invalid ID number or password."
        except Signup.DoesNotExist:
            error = "User not found."
        
        return render(request, 'login/LOGIN.html', {'error': error})  # Render login page with error
    
    return render(request, 'login/LOGIN.html')  # Initial GET request

def student_status(request):
    # Check if the user is logged in and has an ID in the session
    user_id = request.session.get('user_id')  # Adjust based on your login session setup

    if user_id:
        # Retrieve the logged-in user's data
        user = Signup.objects.get(id=user_id)

         # Retrieve reports filed by the logged-in user, ordered by the most recent incident date
        user_reports = Report.objects.filter(student=user).order_by('-incident_date')

        context = {
            'user': user,
            'user_reports': user_reports,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, 'Student Status.html', context)
    else:
        return redirect('login')  # Redirect to login page if not logged in

def report_detail(request, report_id):
    # Get the report by ID or show a 404 error if not found
    report = get_object_or_404(Report, id=report_id)
    context = {
        'report': report
    }
    return render(request, 'report_detail.html', context)

    
def update_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in first.")
        return redirect('login')

    try:
        user = Signup.objects.get(id=user_id)
    except Signup.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if current_password != user.password:
            messages.error(request, "Current password is incorrect.")
            return render(request, 'Student Settings.html', {'user': user})
        
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'Student Settings.html', {'user': user})
        
        user.password = new_password
        user.save()
        messages.success(request, "Password updated successfully. Please log in again.")
        request.session.flush()
        return redirect('login')

    return render(request, 'Student Settings.html', {'user': user})

def signup(request):
    if request.method == "POST":
        form = SignupNow(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            return redirect('registration_success')  # Ensure you create this page or change this to your homepage

    else:
        form = SignupNow()

    return render(request,'login/Sign-up.html', {'form': form})

def studentstatus(request):
    return render(request, 'Student Status.html')

def studentsettings(request):
    return render(request, 'Student Settings.html')

def manage_dropdown(request):
    if request.method == 'POST':
        # Add a new program
        if 'add_program' in request.POST:
            new_program = request.POST.get('new_program')
            if new_program:
                DropdownOption.objects.create(program1=new_program)
                return redirect('manageprogram')

        # Add a new course
        if 'add_course' in request.POST:
            new_course = request.POST.get('new_course')
            program_id = request.POST.get('program_id')
            if new_course and program_id:
                program = DropdownOption.objects.get(id=program_id)
                Course.objects.create(program=program, course_name=new_course)
                return redirect('manageprogram')

        # Add a new section
        if 'add_section' in request.POST:
            new_section = request.POST.get('new_section')
            course_id = request.POST.get('course_id')
            if new_section and course_id:
                course = Course.objects.get(id=course_id)
                Section.objects.create(course=course, section_name=new_section)
                return redirect('manageprogram')

        # Delete a program
        if 'delete_program' in request.POST:
            program_id = request.POST.get('delete_program')
            DropdownOption.objects.filter(id=program_id).delete()
            return redirect('manageprogram')

        # Delete a course
        if 'delete_course' in request.POST:
            course_id = request.POST.get('delete_course')
            Course.objects.filter(id=course_id).delete()
            return redirect('manageprogram')

        # Delete a section
        if 'delete_section' in request.POST:
            section_id = request.POST.get('delete_section')
            Section.objects.filter(id=section_id).delete()
            return redirect('manageprogram')

    # Fetch all options for the dropdowns
    program_options = DropdownOption.objects.all()
    course_options = Course.objects.all()
    section_options = Section.objects.all()

    return render(request, 'manage_dropdown.html', {
        'program_options': program_options,
        'course_options': course_options,
        'section_options': section_options,
    })

def file_report(request):
    violation_types = ViolationType.objects.all()
    students = Signup.objects.all()

    search_result = None
    selected_student = None  # Initialize selected student ID

    if request.method == 'POST':
        if 'student_id_search' in request.POST:
            # Handle search by student ID
            student_id = request.POST.get('student_id_search')
            try:
                search_result = Signup.objects.get(idnumber=student_id)
                selected_student = search_result.id  # Set the searched student's ID
            except Signup.DoesNotExist:
                search_result = None
        else:
            # Handle form submission
            student_id = request.POST.get('student')
            incident_date = request.POST.get('incident_date')
            violation_type_id = request.POST.get('violation_type')
            
            try:
                student = Signup.objects.get(id=student_id)
                violation_type = ViolationType.objects.get(id=violation_type_id)
                
                context = {
                    'student_id': student.idnumber,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'incident_date': incident_date,
                    'violation_type': violation_type.name,
                    'db_student_id': student_id,
                    'db_violation_type_id': violation_type_id,
                }
                return render(request, 'report_summary.html', context)
            except (Signup.DoesNotExist, ViolationType.DoesNotExist) as e:
                return HttpResponse(f"Error: {str(e)}", status=400)

    return render(request, 'file_report.html', {
        'violation_types': violation_types,
        'students': students,
        'search_result': search_result,
        'selected_student': selected_student,
    })



def report_summary(request):
    if request.method == 'POST':
        if 'confirm_submission' in request.POST:
            try:
                # Create and save the report
                report = Report.objects.create(
                    student_id=request.POST.get('db_student_id'),
                    incident_date=request.POST.get('incident_date'),
                    violation_type_id=request.POST.get('db_violation_type_id')
                )
                return redirect('report_success')
            except Exception as e:
                return HttpResponse(f"Error saving report: {str(e)}", status=500)
        
        elif 'cancel_submission' in request.POST:
            return redirect('file_report')
    
    return redirect('file_report')

def report_success(request):
    return render(request, 'report_success.html')

def report_summary2(request):
    # Get the violation type name from GET parameters
    violation_type_name = request.GET.get('violation_type')  

    # Try to fetch the ViolationType object
    try:
        violation_type = ViolationType.objects.get(name=violation_type_name)
        context = {
            'violation_type': violation_type,
            'sanction_period_value': violation_type.sanction_period_value,
            'sanction_period_type': violation_type.sanction_period_type,
            'sanction': violation_type.sanction,
        }
    except ViolationType.DoesNotExist:
        context = {
            'error_message': 'Violation Type not found.'
        }

    # Get student data from GET parameters
    student_id = request.GET.get('student_id')
    student_name = None  # Initialize student_name

    if student_id:
        try:
            # Fetch the student from the Signup model using student_id
            student = Signup.objects.get(id=student_id)
            student_name = f"{student.first_name} {student.last_name}"  # Combine first and last name
        except Signup.DoesNotExist:
            student_name = 'Unknown Student'  # Fallback if the student is not found

    # Add student data to the context without overwriting the previous data
    context.update({
        'student_id': student_id,
        'student_name': student_name,
        'incident_date': request.GET.get('incident_date'),
        'violation_type': violation_type_name,
    })

    # Render the template with the combined context
    return render(request, 'report_summary2.html', context)

def report_success(request):
    return render(request, 'report_success.html')

# Manage Violations (for admins)
def manage_violations(request):
    violations = ViolationType.objects.all()
    if request.method == 'POST':
        form = ViolationTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_violations')
    else:
        form = ViolationTypeForm()

    return render(request, 'manage_violations.html', {'form': form, 'violations': violations})

# Edit Violation
def edit_violation(request, violation_id):
    violation = ViolationType.objects.get(id=violation_id)
    if request.method == 'POST':
        form = ViolationTypeForm(request.POST, instance=violation)
        if form.is_valid():
            form.save()
            return redirect('manage_violations')
    else:
        form = ViolationTypeForm(instance=violation)

    return render(request, 'edit_violation.html', {'form': form, 'violation': violation})

def reset(request):
    return render(request, 'login/Reset Password.html')

def resetconfirmation(request):
    return render(request, 'login/Reset Password Confirmation.html')

def forget(request):
    return render(request, 'login/Forget Password.html')

def change(request):
    return render(request, 'login/ForceChange.html')

def code(request):
    return render(request, 'login/Enter Code.html')
#------ studentmod ------
def infopop(request):
    return render(request, 'infopopup.html')

def monitorrep(request):
    return render(request, 'MonitorReport.html')

def reportsumstud(request):
    return render(request, 'studentmod/ReportSummaryStudent.html')

def infopopup3(request):
    return render(request, 'studentmod/infopopup3.html')

#------- guard and instructor module ------
def registration_success(request):
    return render(request, 'registration_success.html')

def report_success(request):
    return render(request, 'report_success.html')

def changepass(request):
    return render(request,'Changepass.html')

def violationreports(request):
    # Fetch all dropdown options (programs)
    programs = DropdownOption.objects.all()
    
    # Fetch all violation types
    violations = ViolationType.objects.all()
    
    # Fetch all distinct sanctions (from ViolationType)
    sanctions = ViolationType.objects.values_list('sanction', flat=True).distinct()

    # Fetch the reports (apply filters based on the selected criteria if any)
    reports = Report.objects.select_related('student', 'violation_type')

    # Apply the filters based on request parameters
    status_filter = request.GET.get('filter_status')
    program_filter = request.GET.get('filter_program')
    month_filter = request.GET.get('filter_date')
    violation_filter = request.GET.get('filter_violation')
    sanction_filter = request.GET.get('filter_sanction')

    if status_filter:
        reports = reports.filter(status=status_filter)
        
    if program_filter:
        reports = reports.filter(student__program1_id=program_filter)

    if month_filter:
        year, month = map(int, month_filter.split('-'))
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, 1) + datetime.timedelta(days=32)
        end_date = end_date.replace(day=1) - datetime.timedelta(days=1)
        reports = reports.filter(incident_date__range=(start_date, end_date))

    if violation_filter:
        reports = reports.filter(violation_type__name=violation_filter)

    if sanction_filter:
        reports = reports.filter(violation_type__sanction=sanction_filter)

    # Pass the necessary data to the template
    context = {
        'reports': reports,
        'programs': programs,
        'violations': violations,
        'sanctions': sanctions,
        'request': request,  # Pass the request object to the template
    }

    return render(request, 'violationreports.html', context)

def update_status(request, report_id):
    if request.method == 'POST':
        # Get the report object
        report = get_object_or_404(Report, id=report_id)
        
        # Get the new status from the form
        new_status = request.POST.get('status')
        
        # Update the report status
        report.status = new_status
        report.save()
        
        # Redirect back to the reports page
        return redirect('violationreports')
    
    return HttpResponse("Invalid request", status=400)

def account_approval(request):
    return render(request, "account_approval.html")

def filter(request):
    return render(request, "filter.html")

def filter_accounts(request):
    search_id = request.GET.get('search', '')
    students = Signup.objects.filter(idnumber__icontains=search_id)
    return render(request, 'filter.html', {'students': students})

def approve_student(request, student_id):
    student = get_object_or_404(Signup, id=student_id)
    try:
        with transaction.atomic():
            ApprovedStudent.objects.create(
                first_name=student.first_name,
                middle_initial=student.middle_initial,
                last_name=student.last_name,
                idnumber=student.idnumber,
                email=student.email,
                program1=student.program1,
                course=student.course,
                section=student.section,
                id_picture=student.id_picture,
                registration_cert=student.registration_cert,
            )
            student.delete()  # Remove from Signup after approval
    except Exception as e:
        pass  # Optionally log error
    return redirect('filter')

def reject_student(request, student_id):
    student = get_object_or_404(Signup, id=student_id)
    try:
        with transaction.atomic():
            RejectedStudent.objects.create(
                first_name=student.first_name,
                middle_initial=student.middle_initial,
                last_name=student.last_name,
                idnumber=student.idnumber,
                email=student.email,
                program1=student.program1,
                course=student.course,
                section=student.section,
                id_picture=student.id_picture,
                registration_cert=student.registration_cert,
            )
            student.delete()  # Remove from Signup after rejection
    except Exception as e:
        pass  # Optionally log error
    return redirect('filter')

def staff_list(request):
    staff_members = Userrole.objects.all()  # Fetch all Userrole instances
    return render(request, 'staff_list.html', {'staff_members': staff_members})

from django.shortcuts import render
from .models import Userrole# Assuming your model is named `Userrole`

def staff_list(request):
    query = request.GET.get('query', '')
    if query:
        staff_members = Userrole.objects.filter(
            first_name__icontains=query
        ) | Userrole.objects.filter(
            last_name__icontains=query
        ) | Userrole.objects.filter(
            employee_id__icontains=query
        ) | Userrole.objects.filter(
            email__icontains=query
        ) | Userrole.objects.filter(
            position__icontains=query
        )
    else:
        staff_members = Userrole.objects.all()
    
    return render(request, 'staff_list.html', {'staff_members': staff_members})

