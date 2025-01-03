from django.contrib import admin
from .models import Chat, ChatMetric, AggregatedChatMetric, ChatSetting

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass

@admin.register(ChatMetric)
class ChatMetricAdmin(admin.ModelAdmin):
    pass

@admin.register(AggregatedChatMetric)
class AggregatedChatMetricAdmin(admin.ModelAdmin):
    pass

@admin.register(ChatSetting)
class ChatSettingAdmin(admin.ModelAdmin):
    pass