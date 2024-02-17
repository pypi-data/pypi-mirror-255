from django.db import models

class Task(models.Model):
    OPEN = 'open'
    CLOSED = 'closed'
    IN_PROGRESS = 'inprogress'
    STATUS_CHOICES = [(OPEN,'Open'), (CLOSED, 'Closed'), (IN_PROGRESS, 'In Progress')]
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, default=OPEN)

    def __str__(self):
        return self.title


class SubTask(models.Model):
    OPEN = 'open'
    CLOSED = 'closed'
    IN_PROGRESS = 'inprogress'
    STATUS_CHOICES = [(OPEN,'Open'), (CLOSED, 'Closed'), (IN_PROGRESS, 'In Progress')]
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, default=OPEN)


    def __str__(self):
        return self.title
