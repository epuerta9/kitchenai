from django.db import models
from falco_toolbox.models import TimeStamped

def module_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/filename
    return f"kitchenai/modules/{filename}"

class KitchenAIManagement(TimeStamped):
    name = models.CharField(max_length=255, primary_key=True, default="kitchenai_management")
    project_name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    description = models.TextField(default="")
    module_path = models.CharField(max_length=255, default="bento")
    jupyter_token = models.CharField(max_length=255, default="")
    jupyter_host = models.CharField(max_length=255, default="localhost")
    jupyter_port = models.CharField(max_length=255, default="8888")
    jupyter_protocol = models.CharField(max_length=255, default="http")

    def __str__(self):
        return self.name


class KitchenAIPlugins(TimeStamped):
    name = models.CharField(max_length=255, unique=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class KitchenAIRootModule(TimeStamped):
    name = models.CharField(max_length=255, unique=True)
    kitchen = models.ForeignKey(KitchenAIManagement, on_delete=models.CASCADE)
