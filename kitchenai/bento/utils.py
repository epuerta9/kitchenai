from .models import LoadedBento

def load_bento(bento_name: str, config: dict, settings: dict):
    if LoadedBento.objects.filter(name=bento_name).exists():
        LoadedBento.objects.filter(name=bento_name).delete()
    loaded_bento = LoadedBento.objects.create(name=bento_name, config=config, settings=settings)
    return loaded_bento

def unload_bento(loaded_bento_name: str):
    loaded_bento = LoadedBento.objects.get(name=loaded_bento_name)
    loaded_bento.delete()
    return

def get_loaded_bento(loaded_bento_name: str):
    return LoadedBento.objects.get(name=loaded_bento_name)

