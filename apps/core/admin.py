from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import DaneOperator1


@admin.register(DaneOperator1)
class DaneOperator1Admin(admin.ModelAdmin):
    list_display = ['import_uuid', 'poczatek', 'typ', 'wspolrzedne1_link', 'msisdn1', 'wspolrzedne1','kt1','azymut1','zasig1']
    list_filter = ['typ', 'import_uuid']
    search_fields = ['msisddn1', 'msisdn2', 'imei1']

    def wspolrzedne1_link(self, obj):
        if obj.import_uuid and obj.wspolrzedne1:
            url = reverse('operator1_view', kwargs={'uuid': str(obj.import_uuid)})
            return format_html('<a href="{}" target="_blank">Mapa BTS</a>', url)
        return '-'

    wspolrzedne1_link.short_description = 'Wizualizacja'
