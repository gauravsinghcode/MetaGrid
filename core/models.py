from django.db import models

class TableMetadata(models.Model):

    name = models.CharField(max_length=25, null=False, unique=True)
    is_active = models.BooleanField(default=True, null=False)
    is_synced = models.BooleanField(default=True, null=False)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ColumnMetadata(models.Model):

    table = models.ForeignKey(TableMetadata, on_delete=models.CASCADE, related_name="columns")
    name = models.CharField(max_length=255, null=False)
    data_type = models.CharField(max_length=10, null=False)
    is_active = models.BooleanField(default=True, null=False)
    nullable = models.BooleanField(null=False)
    primary_key = models.BooleanField()
    unique = models.BooleanField()
    default_value = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return f"{self.table.name}.{self.name}"