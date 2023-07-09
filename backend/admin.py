from django.contrib import admin
from backend.models import BotAdmin, Channel, BotUser, Resource


class BotUserAdmin(admin.ModelAdmin):
    list_display = ["chat_id", "first_name", "last_name", "username", "last_seen", "joined"]


class ResourceAdmin(admin.ModelAdmin):
    list_display = ["file_name", "title", "file_type", "publisher", "status"]
    list_filter = ["file_type", "status"]


admin.site.register(BotUser, BotUserAdmin)
admin.site.register(BotAdmin)
admin.site.register(Channel)
admin.site.register(Resource, ResourceAdmin)
