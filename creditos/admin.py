from django.contrib import admin
from .models import ConsentLog

# Register your models here.

@admin.register(ConsentLog)
class ConsentLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "analytics", "expires_at", "ip", "user")
    list_filter = ("action", "analytics", "created_at")
    search_fields = ("ip", "user_agent")
    ordering = ("-created_at",)
