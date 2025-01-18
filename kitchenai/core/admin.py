from django.contrib import admin

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
    pass


@admin.register(OSSOrganization)
class OSSOrganizationAdmin(admin.ModelAdmin):
    pass

@admin.register(OSSOrganizationMember)
class OSSOrganizationMemberAdmin(admin.ModelAdmin):
    pass    

@admin.register(OSSUser)
class OSSKitchenAIUserAdmin(admin.ModelAdmin):
    pass