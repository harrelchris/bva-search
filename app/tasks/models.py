from django.db import models


class Task(models.Model):
    name = models.CharField(max_length=100)
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.datetime}"
