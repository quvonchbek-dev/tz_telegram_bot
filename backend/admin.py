from django.contrib import admin
from backend.models import BotAdmin, Channel, BotUser


class BotUserAdmin(admin.ModelAdmin):
    list_display = ["chat_id", "first_name", "last_name", "username", "last_seen", "joined"]


admin.site.register(BotUser, BotUserAdmin)
admin.site.register(BotAdmin)
admin.site.register(Channel)
