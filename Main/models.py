from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    poster_url = models.URLField()
    release_date = models.DateField()
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.title