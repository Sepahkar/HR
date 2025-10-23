from django.contrib import admin
from HR.models import VirtualUsers
from HR.utils import call_api
import HR.models as HR


@admin.register(VirtualUsers)
class VirtualUsersAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return VirtualUsers.objects.none()

    def changelist_view(self, request, extra_context=None):
        extra_context = {}
        data = call_api(request,"AccessControl","get-all-apps-info")
        all_apps = []
        for item in data:
            for k,v in item.items():
                if v is None:
                    item.update({k:''})
            all_apps.append(item)

        extra_context['all_apps'] = all_apps
        return super(VirtualUsersAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    class Meta:
        model = VirtualUsers


@admin.register(HR.ConstValue)
class ConstValue(admin.ModelAdmin):
    list_display = ('Code', 'Caption', 'Parent')
    list_display_links = ('Code', )
    search_fields = ('Code', 'Caption',)