from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from .models import Task, SubTask
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic


class HomeView(generic.ListView):
    template_name = 'tasksapp/home.html'

    def get_queryset(self):
        return Task.objects.order_by('end_date').all() 

# def home(request):
#     tasks = Task.objects.order_by('end_date').all()
#     return render(request, 'tasksapp/home.html', {'tasks': tasks})


def addtask(request):
    if(request.method == 'POST'):
        title = request.POST['title']
        description = request.POST['description']
        end_date = request.POST['end_date']
        status = 'open'
        Task.objects.create(title=title, description=description,end_date=end_date, status=status)

        return HttpResponseRedirect(reverse('tasksapp:home'))
    return render(request, 'tasksapp/addtask.html')


class TaskView(generic.DetailView):
    model = Task
    template_name = 'tasksapp/viewtask.html'

# def viewtask(request, task_id):
#     task = get_object_or_404(Task, pk=task_id)
#     return render(request, 'tasksapp/viewtask.html', {'task': task})


def addsubtask(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if(request.method == 'POST'):
        subtask_title = request.POST['title']
        subtask_description = request.POST['description']
        subtask_end_date = request.POST['end_date']
        subtask_status = 'open'

        SubTask.objects.create(task_id = task_id, title=subtask_title, description=subtask_description, end_date=subtask_end_date, status=subtask_status)

        return HttpResponseRedirect(reverse("tasksapp:viewtask", args=(task.id,)))
    return render(request, 'tasksapp/addsubtask.html', {'task': task})


def deletetask(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return HttpResponseRedirect(reverse('tasksapp:home')) 


def deletesubtask(request,task_id, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id)
    subtask.delete()
    return HttpResponseRedirect(reverse('tasksapp:viewtask', args=(task_id, ))) 


def changetaskstatus(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.status = request.POST['status']
    task.save()
    return HttpResponseRedirect(reverse('tasksapp:home')) 


def changesubtaskstatus(request,task_id, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id)
    subtask.status = request.POST['status']
    subtask.save()
    return HttpResponseRedirect(reverse('tasksapp:viewtask', args=(task_id, ))) 