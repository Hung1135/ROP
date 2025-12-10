from django.db import models

class Cvs(models.Model):
    id = models.AutoField(primary_key=True)

    candidate_id = models.IntegerField()

    file_name = models.CharField(max_length=255)

    file_path = models.CharField(max_length=500)

    extract_text =models.CharField(max_length=500)

    upload_at = models.DateField(auto_now=True)

    class Meta:
        db_table = 'cvs'
        managed = False   

    def __str__(self):
        return self.file_name
