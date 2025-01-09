from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    rating = models.FloatField()

    def __str__(self):
        return self.title
