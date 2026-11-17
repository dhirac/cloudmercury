from django.contrib import admin
from .models import Contact
# Register your models here.



class ShowContact(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('name','email','subject','message')
    search_fields = Contact.SearchableFields
    

    def has_add_permission(self, request):
        return False

admin.site.register(Contact,ShowContact)