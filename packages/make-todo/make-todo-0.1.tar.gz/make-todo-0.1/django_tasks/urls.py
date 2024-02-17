from django.urls import path
from . import views

app_name='tasksapp'
urlpatterns = [
    path('', views.HomeView.as_view(), name = "home"),
    path('add-task/', views.addtask, name = "addtask"),
    path('<int:pk>/view-task/', views.TaskView.as_view(), name = "viewtask"),
    path('<int:task_id>/add-subtask/', views.addsubtask, name = "addsubtask"),
    path('<int:task_id>/delete-task', views.deletetask, name = "deletetask"),
    path('<int:task_id>/change-task-status', views.changetaskstatus, name = "changetaskstatus"),
    path('<int:task_id>/<int:subtask_id>/delete-subtask', views.deletesubtask, name = "deletesubtask"),
    path('<int:task_id>/<int:subtask_id>/change-subtask-status', views.changesubtaskstatus, name = "changesubtaskstatus")

]