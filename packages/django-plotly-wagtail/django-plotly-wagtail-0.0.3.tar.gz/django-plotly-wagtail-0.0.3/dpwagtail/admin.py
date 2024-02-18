from django.contrib import admin


from .models import (DashInstance, DashInstanceAdmin,
                     InstanceBuilder, InstanceBuilderAdmin,
                     )


admin.site.register(DashInstance, DashInstanceAdmin)
admin.site.register(InstanceBuilder, InstanceBuilderAdmin)
