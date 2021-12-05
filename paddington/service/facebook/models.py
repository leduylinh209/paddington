from django.db import models


class Comment(models.Model):
    comment_id = models.CharField(max_length=256, editable=False, unique=True)

    def __str__(self):
        return "Comment {}".format(self.comment_id)
