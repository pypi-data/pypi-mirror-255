============
django-tasks
============

django-tasks is a Django app to conduct web-based tasks. For each
question, visitors can choose between a fixed number of answers.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "tasks" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "django_tasks",
    ]

2. Include the tasks URLconf in your project urls.py like this::

    path("tasks/", include("django_tasks.urls")),

3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit the admin to create a task.

5. Visit the ``/tasks/`` URL to view the tasks.