from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    #dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    #issue_status
    path('DenyReport/', views.DenyReport, name='DenyReport'),
    #path('ProbationProgress/', views.ProbationProgress, name='ProbationProgress'),
    path('monitorreport/', views.monitorrep, name='monitorreport'),

    #user_role
    path('retry-password/', views.retry_password, name='retry_password'),

    #login
    path('', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('reset/', views.reset, name='reset'),
    path('resetconfirmation/', views.resetconfirmation, name='resetconfirmation'),
    path('forget/', views.forget, name='forget'),
    path('change/', views.change, name='change'),
    path('code/', views.code, name='code'),

    #student mod
    path('studentsettings/'   , views.update_password, name='studentsettings'),
    path('studentstatus/'     , views.student_status, name='studentstatus'),

    #guard and instructor mod
    path('manage-violations/', views.manage_violations, name='manage_violations'),
    path('edit-violation/<int:violation_id>/', views.edit_violation, name='edit_violation'),  
    path('report-success/', views.report_success, name='report_success'),
    path('report-summary/', views.report_summary, name='report_summary'),
    path('manageprogram/', views.manage_dropdown, name='manageprogram'),
    path('registration_success/', views.registration_success, name='registration_success'),
    path('file-report/', views.file_report, name='file_report'),
    path('changepass/', views.changepass, name='changepass'),
    path('violationreports/', views.violationreports, name='violationreports'),
    path('update_status/<int:report_id>/', views.update_status, name='update_status'),
    path('report_summary2/', views.report_summary2, name='report_summary2'), 
    path('account_approval/', views.account_approval, name='account_approval'),
    path('adduser/', views.adduser, name='adduser'),
    path('userrole/', views.userrole, name='userrole'),
    path('edituserrole/', views.edituserrole, name='edituserrole'),
    path("useraccount/",views.useraccount, name="useraccount"),
    path('filter/', views.filter_accounts, name='filter'),
    path('approve/<int:student_id>/', views.approve_student, name='approve_student'),
    path('reject/<int:student_id>/', views.reject_student, name='reject_student'),
    path('staff/', views.staff_list, name='staff_list'),
    path('report_detail/<int:report_id>/', views.report_detail, name='report_detail'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)