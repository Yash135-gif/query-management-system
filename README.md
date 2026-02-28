Query Management System

A full-featured role-based ticket conversation system built using Django, MySQL, HTML and CSS.

This system is not a simple single-question-answer platform.
It is a multi-message conversation-based ticket management system where Users, Employees, and Admins interact in a structured workflow.

📌 Project Overview

The Query Management System is designed to manage customer queries efficiently across departments with structured role-based dashboards.

The system includes:

👤 User Dashboard

👨‍💼 Employee Dashboard

🛠 Admin Dashboard

Each role has its own permissions, features, and workflow logic.

🧑‍💻 Tech Stack

Backend: Python, Django

Database: MySQL

Frontend: HTML, CSS

Authentication: Custom role-based login system

Architecture: Manual role handling (No Django default auth system used)

🎯 Core Features
🔐 Role-Based Dashboard System

The system uses a role field in the database:

user

employee

admin

After login, users are redirected to their respective dashboards based on their role.

👤 User Features

Create new queries

Select department while creating query

Send query directly to Admin (optional)

Participate in conversation until ticket is closed

View own queries

Unlimited messages within a single query

Conversation-based interaction (Not single Q&A)

👨‍💼 Employee Features

View Unclaimed Queries (Department-specific)

Claim a query

Once claimed → Hidden from other employees of same department

View Claimed Queries

Reply to queries

Forward query to Admin

View Forwarded Queries

View Resolved Queries

Create query for Admin

Multi-message conversation support

🛠 Admin Features

View all forwarded queries

Participate in conversation threads

Reply directly to user queries

Close tickets

View employee queries

View resolved queries

View forwarded queries

Manage Employees:

View employee list

Promote user to employee

Complete system-level access

🏢 Department-Based Routing System

When a user creates a query:

User selects a department.

Query becomes visible only to employees of that department.

If one employee claims it:

It disappears from other employees’ unclaimed list.

Ensures proper workload distribution.

💬 Conversation-Based Ticket System

Unlike traditional Q&A systems:

Each query supports unlimited messages

Multiple participants can join (User, Employee, Admin)

Conversation continues until ticket is closed

Works similar to a support thread

🧠 System Workflow
🔹 User → Employee

User creates query → Department employees see it → One employee claims it → Conversation starts.

🔹 Employee → Admin

If employee cannot resolve → Forwards to admin → Admin joins conversation.

🔹 User → Admin

User can directly send query to admin.

🔑 Default Admin Credentials
Email: admin@test.com
Password: admin123
🗄 Database Design Highlights

Custom User model with role field

Department model

Query model

Conversation/message model

Claim logic implementation

Status-based query management (Pending, Forwarded, Resolved, etc.)

📂 Dashboards

The project contains three separate dashboards:

User Dashboard

Employee Dashboard

Admin Dashboard

Each dashboard dynamically loads content using HTML, CSS and radio-button-based UI switching.

🔥 Unique Selling Points (USP)

✔ Role-based redirection logic (Manually implemented)
✔ Department filtering system
✔ Claim-based query handling
✔ Forward-to-admin mechanism
✔ Multi-message ticket conversation
✔ No simple CRUD project — Real workflow-based system

📈 Future Improvements

Email notifications

Real-time chat using WebSockets

File attachments in queries

Dashboard analytics

JWT authentication

REST API integration

🏁 How to Run the Project
git clone <your-repo-link>
cd query-management-system
pip install -r requirements.txt

Configure MySQL database in settings.py.

Then:

python manage.py migrate
python manage.py runserver
