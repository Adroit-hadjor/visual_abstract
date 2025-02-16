How to run this project
----------------------------------------------------------------------



git clone https://github.com/Adroit-hadjor/visual_abstract.git

cd project_management

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

 Usage
----------------------------------------------------------------------

4.1. Login & Signup
----------------------------------------------------------------------

Signup: Navigate to <your-domain>/accounts/signup/ (or if you’re using an HTMX approach, see the relevant partial _signup_form.html).
Login: Navigate to <your-domain>/accounts/login/.
Once logged in, you can access /projects/ (the main index).

4.2. Projects
----------------------------------------------------------------------
Create a Project: Click “Create New Project” (HTMX modal). Submits a POST to project_create.
Edit a Project: Click the Edit button in the right panel (or row). Submits to project_update.
Delete a Project: Press Delete. If you are the owner, it removes the project from the list.
Add Member: Press Add Member in the details area (for owners only). Submits a POST to project_add_member.

4.3. Role-Based Access
----------------------------------------------------------------------
owner: Can edit, delete, add members, etc.
editor: Can edit, add comments, but not delete the project or add new members.
reader: Can only read (view) the project details and comments, but not modify them.

4.4. Comments
----------------------------------------------------------------------
Owners & Editors can add comments (via project_comment_add).
The comment list updates dynamically in the comments container.

5. Running Tests
----------------------------------------------------------------------
We have unit tests for:
Signup
Login
Project creation, update, delete
Add member flow
To run them all:
bash


python manage.py test


Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......
----------------------------------------------------------------------
Ran 9 tests in 0.873s

OK
Destroying test database for alias 'default'...
