from django.contrib import admin
from django.conf import settings


from .models import (
    EmbedObject,
    FileObject,
    KitchenAIManagement,
    EmbedFunctionTokenCounts,
    StorageFunctionTokenCounts,
    OSSOrganization,
    OSSOrganizationMember,
    OSSUser,
    OSSBentoClient,
)

@admin.register(OSSOrganization)
class OSSOrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(OSSUser)
class OSSUserAdmin(admin.ModelAdmin):
    pass

@admin.register(OSSOrganizationMember)
class OSSOrganizationMemberAdmin(admin.ModelAdmin):
    pass


@admin.register(KitchenAIManagement)
class KitchenAIAdmin(admin.ModelAdmin):
    pass


@admin.register(FileObject)
class FileObjectAdmin(admin.ModelAdmin):
    pass


@admin.register(EmbedObject)
class EmbedObjectAdmin(admin.ModelAdmin):
    pass


@admin.register(EmbedFunctionTokenCounts)
class EmbedFunctionTokenCountsAdmin(admin.ModelAdmin):
    pass


@admin.register(StorageFunctionTokenCounts)
class StorageFunctionTokenCountsAdmin(admin.ModelAdmin):
    pass



@admin.register(OSSBentoClient)
class OSSBentoClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_id', 'version', 'get_last_seen', 'ack']
    list_filter = ['version', 'last_seen', 'ack', 'client_type']
    search_fields = ['name', 'client_id', 'client_description']
    readonly_fields = ['last_seen', 'created_at', 'updated_at']
    
    def get_last_seen(self, obj):
        if obj.last_seen:
            return obj.last_seen.strftime("%Y-%m-%d %H:%M:%S")
        return "-"
    get_last_seen.short_description = "Last Seen"
    get_last_seen.admin_order_field = 'last_seen'

    fieldsets = [
        (None, {
            'fields': ['name', 'client_id', 'version']
        }),
        ('Status', {
            'fields': ['ack', 'message', 'last_seen'],
            'classes': ['collapse-open']
        }),
        ('Client Details', {
            'fields': ['client_type', 'client_description'],
            'classes': ['collapse']
        }),
        ('Bento Configuration', {
            'fields': ['bento_box'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

    def has_add_permission(self, request):
        """Disable manual creation as these are created via API"""
        return False