from django.shortcuts import render, redirect, get_object_or_404
from functools import wraps
from django.utils import timezone
from datetime import timedelta
from .models import User, Department, EmployeeProfile, UserQuery, EmployeeQuery,UserQueryMessage,EmployeeQueryMessage
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.

# Mark urgent function

def mark_urgent(queryset):
    now = timezone.now()
    one_day_ago = now - timedelta(hours=24)

    for q in queryset:
        q.is_urgent = q.created_at < one_day_ago

    return queryset

# Email system

def send_notification_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False
    )

# Access decorator

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(req, *args, **kwargs):
            auth = req.session.get('auth')

            if not auth or auth.get('role') != required_role:
                return redirect('login')

            return view_func(req, *args, **kwargs)

        return wrapper
    return decorator


def home(req):
    return render(req,'home.html')

def register(req):
    return render(req,'register.html')

def login(req):
    return render(req,'login.html')

def register_data(req):
    if req.method == "POST":
        n = req.POST.get('name')
        e = req.POST.get('email')
        c = req.POST.get('contact')
        p = req.POST.get('password')
        cp = req.POST.get('confirm_password')

        if User.objects.filter(email=e).exists():
            return render(req, 'register.html', {'message': 'Email already exists'})

        if p != cp:
            return render(req, 'register.html', {'message': 'Passwords must match'})

        hashed_password = make_password(p)

        User.objects.create(
            name=n,
            email=e,
            contact=c,
            password=hashed_password,
            role='user'  
        )

        return redirect('login')

def login_data(req):
    if req.method == "POST":
        email = req.POST.get('email')
        password = req.POST.get('password')

        user = User.objects.filter(email=email).first()

        if user and check_password(password, user.password):

            req.session['auth'] = {
                'user_id': user.id,
                'name': user.name,
                'role': user.role
            }

            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'employee':
                return redirect('employee_dashboard')
            else:
                return redirect('user_dashboard')

        else:
            return redirect('login')

    return redirect('login')

@role_required('employee')
def employee_dashboard(request):
    auth = request.session.get('auth')

    employee_id = auth.get('user_id')

    employee = get_object_or_404(User, id=employee_id)

    queries = UserQuery.objects.filter(
        department=employee.employeeprofile.department
    )

    search = request.GET.get('search')
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')

    if search:
        queries = queries.filter(user__name__icontains=search)

    if status_filter:
        queries = queries.filter(status=status_filter)

    if priority_filter:
        queries = queries.filter(priority=priority_filter)
    
    employee_queries = EmployeeQuery.objects.filter(employee_id=employee_id)

    unclaimed_queries = queries.filter(
        status='pending',
        assigned_employee__isnull=True
    )

    my_active_queries = queries.filter(
        assigned_employee=employee,
        status='in_progress'
    )

    forwarded_queries = queries.filter(
        assigned_employee=employee,
        status='pending_admin'
    )

    resolved_queries = queries.filter(
    assigned_employee=employee,
    status='closed'
)

    unclaimed_queries = mark_urgent(unclaimed_queries)
    my_active_queries = mark_urgent(my_active_queries)
    forwarded_queries = mark_urgent(forwarded_queries)

    context = {
        'unclaimed_queries': unclaimed_queries,
        'my_active_queries': my_active_queries,
        'forwarded_queries': forwarded_queries,
        'resolved_queries': resolved_queries,
        'employee_queries': employee_queries,
        'name':employee.name
    }

    return render(request, 'employee_dashboard.html', context)

@role_required('admin')
def admin_dashboard(req):
    auth = req.session.get('auth')

    total_users = User.objects.filter(role='user').count()
    total_employees = User.objects.filter(role='employee').count()
    total_departments = Department.objects.count()
    total_queries = UserQuery.objects.count() + EmployeeQuery.objects.count()
    pending_queries = (
    UserQuery.objects.filter(
    status__in=['pending', 'in_progress', 'pending_admin']
).count()
    + EmployeeQuery.objects.filter(status__in=['pending', 'in_progress', 'pending_admin']).count()
)
    return render(req, 'admin_dashboard.html', {
        'name': auth['name'],
        'total_users': total_users,
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_queries': total_queries,
        'pending_queries': pending_queries
    })


def logout_view(req):
    if 'auth' in req.session:
       req.session.flush() 
    return redirect('login')

@role_required('user')
def user_dashboard(req):
    auth = req.session.get('auth')
    return render(req, 'user_dashboard.html', {'name': auth['name']})

@role_required('user')
def my_queries(req):
    auth = req.session.get('auth')
    user_id = auth.get('user_id')

    queries = UserQuery.objects.filter(user_id=user_id,is_deleted=False).order_by('-created_at')

    return render(req, 'my_queries.html', {'queries': queries})

@role_required('user')
def user_add_query(req):
    departments = Department.objects.all()

    if req.method == "POST":
        auth = req.session.get('auth')
        user_id = auth.get('user_id')

        department_id = req.POST.get('department_id')
        title = req.POST.get('question')  # temporarily same textarea use kar rahe
        attachment = req.FILES.get('attachment')

        department = Department.objects.get(id=department_id)      

        query = UserQuery.objects.create(
            user_id=user_id,
            department=department,
            assigned_employee=None,
            title=title,
            status='pending'
        )


        # 🔥 First message create karo
        UserQueryMessage.objects.create(
            query=query,
            sender_id=user_id,
            message=title,
            attachment=attachment
        )

        return redirect('user_dashboard')

    return render(req, 'user_add_query.html', {
        'departments': departments
    })

@role_required('employee')
def employee_reply_query(req, query_id):

    auth = req.session.get('auth')
    employee_id = auth.get('user_id')

    query = get_object_or_404(
        UserQuery,
        id=query_id,
        is_deleted=False
    )

    employee_profile = get_object_or_404(
        EmployeeProfile,
        user_id=employee_id
    )
 
    if query.department != employee_profile.department:
        return redirect('employee_dashboard')
 
    if query.assigned_employee and query.assigned_employee.id != employee_id:
        return redirect('employee_dashboard')
 
    if query.status == 'closed':
        return redirect('employee_dashboard')

    if req.method == "POST":
        action = req.POST.get('action')
        attachment = req.FILES.get('attachment')
        if not query.assigned_employee:
            return redirect('employee_dashboard')
 
        if action == "reply":

            reply_text = req.POST.get('reply')

            if not reply_text:
                return render(req, 'employee_reply.html', {
                    'query': query,
                    'error': "Reply cannot be empty."
                })

            UserQueryMessage.objects.create(
                query=query,
                sender_id=employee_id,
                message=reply_text,
                attachment=attachment
            )

            
            subject = "Your Query has been answered!"
            message = f"Hi {query.user.name},\n\nYou have a new reply on your query.\nCheck dashboard."
            send_notification_email(subject, message, [query.user.email])
                 
            query.status = "in_progress"

        elif action == "forward":
            forward_note = req.POST.get('reply')

            UserQueryMessage.objects.create(
                query=query,
                sender_id=employee_id,
                message=forward_note or "Forwarded to Admin",
                attachment=attachment
            )

            query.status = "pending_admin"
            query.forwarded_to_admin = True
            
        elif action == "close":
            closing_note = req.POST.get('reply')

            UserQueryMessage.objects.create(
                query=query,
                sender_id=employee_id,
                message=closing_note or "Query closed by employee."
            )

            query.status = "closed"

        query.save()

    return render(req, 'employee_reply.html', {
        'query': query
    })

@role_required('user')
def user_reply_query(req, query_id):

    query = get_object_or_404(
    UserQuery,
    id=query_id,
    is_deleted=False
)

    auth = req.session.get('auth')
    user_id = auth.get('user_id')

    if query.status == "closed":
        return render(req, 'user_query_detail.html', {
        'query': query,
        'error': "This ticket is closed. You cannot reply."
    })

    if query.status == "closed":
        return redirect('user_query_detail')

    if req.method == "POST":
        message = req.POST.get('message')
        attachment = req.FILES.get('attachment')

        UserQueryMessage.objects.create(
            query=query,
            sender_id=user_id,
            message=message,
            attachment=attachment
        )

        if query.status == "closed":
            return redirect('my_queries')

        query.save()

        return redirect('user_reply_query', query_id=query.id)

    return render(req, "user_query_detail.html", {"query": query})

@role_required('employee')
def employee_add_query_admin(req):
    if req.method == "POST":
        auth = req.session.get('auth')
        employee_id = auth.get('user_id')

        question = req.POST.get('question')
        attachment = req.FILES.get('attachment')

         
        query = EmployeeQuery.objects.create(
        employee_id=employee_id,
        question=question,
        status="pending"
    )

        EmployeeQueryMessage.objects.create(
            query=query,
            sender_id=employee_id,
            sender_role="employee",
            message=question,
            attachment=attachment
        )

        return redirect('employee_dashboard')

    return render(req, 'employee_add_query_admin.html')

@role_required('admin')
def admin_employee_queries(req):

    status_filter = req.GET.get('status')
    search_query = req.GET.get('search')
    department_filter = req.GET.get('department')

    queries = EmployeeQuery.objects.filter(is_deleted=False).order_by('-created_at')

    if status_filter and status_filter != "All":
        queries = queries.filter(status=status_filter)

    if search_query:
        queries = queries.filter(employee__name__icontains=search_query)

    if department_filter and department_filter != "All":
        queries = queries.filter(
            employee__employeeprofile__department__id=department_filter
        )

    departments = Department.objects.all()

    return render(req, 'admin_employee_queries.html', {
        'queries': queries,
        'selected_status': status_filter,
        'search_value': search_query,
        'departments': departments,
        'selected_department': department_filter
    })

@role_required('admin')
def admin_edit_employee_message(req, message_id):

    message = get_object_or_404(EmployeeQueryMessage, id=message_id)

    last_message = message.query.messages.last()

    if message != last_message:
        return redirect('admin_reply_employee_query', message.query.id)

    if message.sender_role != "admin":
        return redirect('admin_reply_employee_query', message.query.id)

    if req.method == "POST":
        new_text = req.POST.get("message")

        if new_text:
            message.message = new_text
            message.save()

        return redirect('admin_reply_employee_query', message.query.id)

    return render(req, "edit_message.html", {"message": message})

@role_required('employee')
def employee_edit_admin_message(req, message_id):

    message = get_object_or_404(EmployeeQueryMessage, id=message_id)

    last_message = message.query.messages.last()

    if message != last_message:
        return redirect('employee_reply_admin_query', message.query.id)

    if message.sender_role != "employee":
        return redirect('employee_reply_admin_query', message.query.id)

    if req.method == "POST":
        new_text = req.POST.get("message")

        if new_text:
            message.message = new_text
            message.save()

        return redirect('employee_reply_admin_query', message.query.id)

    return render(req, "edit_message.html", {"message": message})

@role_required('admin')
def admin_reply_employee_query(req, query_id):

    query = get_object_or_404(EmployeeQuery, id=query_id)

    messages = query.messages.all()
 
    if query.status == "closed":
        return redirect('admin_employee_queries')
 
    if query.status == "pending":
        query.status = "in_progress"
        query.save()

    if req.method == "POST":
        reply = req.POST.get('reply')
        attachment = req.FILES.get('attachment')

        if reply or attachment:
            EmployeeQueryMessage.objects.create(
                query=query,
                sender_id=req.session.get('auth').get('user_id'),

                sender_role='admin',
                message=reply,
                attachment=attachment
            )
 
            if query.status in ["pending", "in_progress"]:
                query.status = "pending_admin"

            query.save()

        return redirect('admin_reply_employee_query', query_id=query.id)

    return render(req, 'admin_reply_employee_chat.html', {
        'query': query,
        'messages': messages
    })

# def employee_admin_query_chat(request, query_id):
#     query = get_object_or_404(EmployeeQuery, id=query_id)
#     messages = query.messages.all().order_by("created_at")

#     return render(request, "employee_reply_admin_chat.html", {
#         "query": query,
#         "messages": messages
#     })

from django.db.models import Q

@role_required('admin')
def manage_users(req):

    search_query = req.GET.get('search')

    users = User.objects.filter(role='user').order_by('name')

    if search_query:
        users = users.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    return render(req, 'manage_users.html', {
        'users': users,
        'search_value': search_query
    })

@role_required('admin')
def make_employee(req, user_id):
    user = get_object_or_404(User, id=user_id)
    departments = Department.objects.all()

    if user.role == 'employee':
        return redirect('manage_users')

    if req.method == "POST":
        department_id = req.POST.get('department')
        department = get_object_or_404(Department, id=department_id)

        user.role = 'employee'
        user.save()

        EmployeeProfile.objects.get_or_create(
            user=user,
            defaults={'department': department}
        )

        subject = "You are now an Employee!"
        message = f"Hi {user.name},\n\nYou have been promoted to an Employee in department: {department.name}.\nLogin and check your dashboard."
        send_notification_email(subject, message, [user.email])

        return redirect('admin_dashboard')

    return render(req, 'assign_department.html', {
        'user': user,
        'departments': departments
    })

@role_required('employee')
def claim_query(req, query_id):

    auth = req.session.get('auth')
    employee_id = auth.get('user_id')

    query = get_object_or_404(
        UserQuery,
        id=query_id,
        is_deleted=False,
        assigned_employee__isnull=True
    )

    employee_profile = get_object_or_404(
        EmployeeProfile,
        user_id=employee_id
    )
 
    if query.department != employee_profile.department:
        return redirect('employee_dashboard')

    query.assigned_employee_id = employee_id
    query.status = "in_progress"
    query.save()

    return redirect('employee_dashboard')

@role_required('admin')
def admin_user_queries(req):

    queries = UserQuery.objects.filter(
    forwarded_to_admin=True,
    is_deleted=False
).exclude(status="closed").order_by('-created_at')

    return render(req, 'admin_user_queries.html', {
        'queries': queries
    })
@role_required('admin')
def admin_reply_user_query(req, query_id):

    query = get_object_or_404(
    UserQuery,
    id=query_id,
    forwarded_to_admin=True,
    is_deleted=False
)

    if query.status == "closed":
        return redirect('admin_user_queries')
    if req.method == "POST":

        action = req.POST.get("action")
 
        if action == "reply":

            admin_reply = req.POST.get('admin_reply')
            attachment = req.FILES.get('attachment')

            UserQueryMessage.objects.create(
                query=query,
                sender_id=req.session['auth']['user_id'],
                message=admin_reply,
                attachment=attachment
            )
            
            query.status = "in_progress"
             
            query.save()

            subject = "Admin Replied to Your Query"
            message = f"Hi {query.user.name},\n\nAdmin has replied to your query.\nCheck dashboard."
            send_notification_email(subject, message, [query.user.email])
 
        elif action == "close":

            UserQueryMessage.objects.create(
                query=query,
                sender_id=req.session['auth']['user_id'],
                message="Query has been officially closed by Admin."
            )

            query.status = "closed"
            query.forwarded_to_admin = False
            query.save()

        return redirect('admin_user_queries')

    messages = query.messages.all()

    return render(req, 'admin_reply_user.html', {
        'query': query,
        'messages': messages,
        'admin_id': req.session['auth']['user_id']
    })

def add_department(req):
    departments = Department.objects.all()

    if req.method == "POST":
        name = req.POST.get('name')

        if name and not Department.objects.filter(name__iexact=name).exists():
            Department.objects.create(name=name)

        return redirect('add_department')

    return render(req, 'add_department.html', {
        'departments': departments
    })

@role_required('employee')
def edit_employee_last_message(req, query_id):

    auth = req.session.get('auth')
    employee_id = auth.get('user_id')

    query = get_object_or_404(UserQuery, id=query_id)

    if query.status == "closed":
        return redirect('employee_reply', query_id=query.id)

    last_message = query.messages.order_by('-created_at').first()

    if not last_message or last_message.sender_id != employee_id:
        return redirect('employee_reply', query_id=query.id)

    if not last_message:
        return redirect('employee_reply', query_id=query.id)

    if req.method == "POST":
        new_text = req.POST.get('message')

        if new_text:
            last_message.message = new_text
            last_message.save()

        return redirect('employee_reply_query', query_id=query.id)

    return render(req, 'edit_employee_message.html', {
        'message': last_message,
        'query': query
    })

@role_required('employee')
def edit_employee_query(req, query_id):

    auth = req.session.get('auth')
    employee_id = auth.get('user_id')

    query = get_object_or_404(EmployeeQuery, id=query_id, employee_id=employee_id)

    if query.status == "closed":
        return redirect('employee_dashboard')

    if req.method == "POST":
        query.question = req.POST.get('question')
        query.attachment = req.FILES.get('attachment') or query.attachment
        query.save()
        return redirect('employee_dashboard')

    return render(req, 'edit_employee_query.html', {'query': query})

@role_required('employee')
def delete_employee_query(req, query_id):

    auth = req.session.get('auth')
    employee_id = auth.get('user_id')

    query = get_object_or_404(EmployeeQuery, id=query_id, employee_id=employee_id)

    if query.status == "closed":
        return redirect('employee_dashboard')

    query.delete()
    return redirect('employee_dashboard')

@role_required('user')
def edit_user_last_message(req, query_id):

    auth = req.session.get('auth')
    user_id = auth.get('user_id')

    query = get_object_or_404(
        UserQuery,
        id=query_id,
        user_id=user_id
    )
 
    if query.status == "closed":
        return redirect('user_query_detail', query_id=query.id)
 
    last_message = query.messages.order_by('-created_at').first()
 
    if not last_message or last_message.sender_id != user_id:
        return redirect('user_query_detail', query_id=query.id)

    if req.method == "POST":
        new_text = req.POST.get('message')

        if new_text:
            last_message.message = new_text
            last_message.save()

        return redirect('user_query_detail', query_id=query.id)

    return render(req, 'edit_user_message.html', {
        'message': last_message,
        'query': query
    })

@role_required('admin')
def edit_admin_message(req, message_id):

    message = get_object_or_404(UserQueryMessage, id=message_id)
 
    if message.sender.role != "admin":
        return redirect("admin_dashboard")

    query = message.query
 
    if query.status == "closed":
        return redirect("admin_dashboard")
 
    last_message = query.messages.last()

    if last_message.id != message.id:
        return redirect("admin_dashboard")

    if req.method == "POST":
        new_text = req.POST.get("message")
        attachment = req.FILES.get("attachment")

        message.message = new_text

        if attachment:
            message.attachment = attachment

        message.save()

        return redirect("admin_reply_user_query", query.id)

    return render(req, "edit_admin_message.html", {
        "message": message
    })

# @role_required('user')
# def edit_user_query(req, query_id):

    auth = req.session.get('auth')
    user_id = auth.get('user_id')

    query = get_object_or_404(
        UserQuery,
        id=query_id,
        user_id=user_id,
        is_deleted=False
    )

     
    if query.status != "pending" or query.assigned_employee:
        return redirect('my_queries')

    if req.method == "POST":
        query.question = req.POST.get('question')
        query.department_id = req.POST.get('department')
        query.attachment = req.FILES.get('attachment') or query.attachment
        query.save()
        return redirect('my_queries')

    departments = Department.objects.all()

    return render(req, 'edit_user_query.html', {
        'query': query,
        'departments': departments
    })

@role_required('user')
def delete_user_query(req, query_id):

    auth = req.session.get('auth')
    user_id = auth.get('user_id')

    query = get_object_or_404(
        UserQuery,
        id=query_id,
        user_id=user_id,
        is_deleted=False
    )

    if query.status != "pending" or query.assigned_employee:
        return redirect('my_queries')

    query.is_deleted = True
    query.save()

    return redirect('my_queries')

@role_required('admin')
def admin_delete_employee_query(req, query_id):

    query = get_object_or_404(EmployeeQuery, id=query_id)

    query.is_deleted = True
    query.save()

    return redirect('admin_employee_queries')

def show_employees(request):
    employees = EmployeeProfile.objects.select_related('user', 'department')
    
    return render(request, 'show_employees.html', {
        'employees': employees
    })

@role_required('user')
def user_query_detail(req, query_id):

    auth = req.session.get('auth')
    user_id = auth.get('user_id')

    query = get_object_or_404(
        UserQuery,
        id=query_id,
        user_id=user_id,
        is_deleted=False
    )

    if req.method == "POST":
        message = req.POST.get("message")
        attachment = req.FILES.get("attachment")

        UserQueryMessage.objects.create(
            query=query,
            sender_id=req.session['auth']['user_id'],
            message=message,
            attachment=attachment
        )

        if query.status != "pending_admin":
            query.status = "pending"
        query.save()

        return redirect("user_query_detail", query_id=query.id)

    return render(req, "user_query_detail.html", {
        "query": query
    })

@role_required('employee')
def employee_reply_admin_query(req, query_id):

    auth = req.session.get('auth')
    employee_id = auth.get('user_id')

    query = get_object_or_404(EmployeeQuery, id=query_id, employee_id=employee_id)

    messages = EmployeeQueryMessage.objects.filter(query=query).order_by('created_at')

    if req.method == "POST":
        message = req.POST.get('message')
        attachment = req.FILES.get('attachment')

        if message or attachment:
            EmployeeQueryMessage.objects.create(
                query=query,
                sender_id=employee_id,
                sender_role="employee",
                message=message,
                attachment=attachment
            )

            if query.status == "pending_admin":
                query.status = "in_progress"
                query.save()

        return redirect('employee_reply_admin_query', query_id=query.id)

    return render(req, 'employee_reply_admin_chat.html', {
        'query': query,
        'messages': messages
    })

@role_required('employee')
def close_employee_query(req, query_id):

    auth = req.session.get('auth')
    employee_id = auth.get('user_id')

    query = get_object_or_404(EmployeeQuery, id=query_id, employee_id=employee_id)

    query.status = "closed"
    query.save()

    return redirect('employee_dashboard')

@role_required('admin')
def admin_close_query(req, query_id):

    query = get_object_or_404(EmployeeQuery, id=query_id)

    if req.method == "POST":

        query.status = "closed"
        query.save()

        EmployeeQueryMessage.objects.create(
            query=query,
            sender_id=req.session.get('auth').get('user_id'),
            sender_role="admin",
            message=f"Ticket closed by Admin at {timezone.now().strftime('%d %b %Y %I:%M %p')}"
        )

    return redirect('admin_reply_employee_query', query_id=query.id)