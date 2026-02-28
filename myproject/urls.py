"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('register_data/',views.register_data,name='register_data'),
    path('login_data/',views.login_data,name='login_data'),
    path('employee_dashboard/',views.employee_dashboard,name='employee_dashboard'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user_add_query/', views.user_add_query, name='user_add_query'),
    path('employee_reply/<int:query_id>/', views.employee_reply_query, name='employee_reply_query'),
    path('admin_employee_queries/', views.admin_employee_queries, name='admin_employee_queries'),
    path('admin_reply_employee/<int:query_id>/', views.admin_reply_employee_query, name='admin_reply_employee_query'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('make_employee/<int:user_id>/', views.make_employee, name='make_employee'),
    path('claim_query/<int:query_id>/', views.claim_query, name='claim_query'),
    path('my_queries/', views.my_queries, name='my_queries'),
    path('employee_add_query_admin/', views.employee_add_query_admin, name='employee_add_query_admin'),
    path('admin_user_queries/', views.admin_user_queries, name='admin_user_queries'),
    path('admin_reply_user/<int:query_id>/', views.admin_reply_user_query, name='admin_reply_user_query'),
    path('admin_dashboard/add_department/', views.add_department, name='add_department'),
    path('employee/edit-query/<int:query_id>/', views.edit_employee_query, name='edit_employee_query'),
    path('employee/delete-query/<int:query_id>/', views.delete_employee_query, name='delete_employee_query'),
    # path('user/edit-query/<int:query_id>/', views.edit_user_query, name='edit_user_query'),
    path('user/delete-query/<int:query_id>/', views.delete_user_query, name='delete_user_query'),
    path('admin_dashboarad/delete-employee-query/<int:query_id>/',views.admin_delete_employee_query,name='admin_delete_employee_query'),
    path('admin_dashboard/show-employees/', views.show_employees, name='show_employees'),
    path("user-query/<int:query_id>/", views.user_query_detail, name="user_query_detail"),
    path('user/query/<int:query_id>/',views.user_reply_query,name='user_reply_query'),
    path('employee/query/<int:query_id>/edit-last/',views.edit_employee_last_message,name='edit_employee_last_message'),
    path('user/query/<int:query_id>/edit-last/',views.edit_user_last_message,name='edit_user_last_message'),
    path("admin_dashboard/edit-message/<int:message_id>/",views.edit_admin_message,name="edit_admin_message"),
    path('employee/query/<int:query_id>/chat/',views.employee_reply_admin_query,name='employee_reply_admin_query'),
    path('employee/query/<int:query_id>/close/',views.close_employee_query,name='close_employee_query'),
    path('admin_dashboard/query/<int:query_id>/close/',views.admin_close_query,name='admin_close_query'),
    # path('employee/admin-query/<int:query_id>/',views.employee_admin_query_chat,name='employee_admin_query_chat'),
    path("admin_dashboard/edit/<int:message_id>/",views.admin_edit_employee_message,name="admin_edit_employee_message"),
    path("employee/edit-message/<int:message_id>/",views.employee_edit_admin_message,name="employee_edit_admin_message"),
    path('logout/', views.logout_view, name='logout'),    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
