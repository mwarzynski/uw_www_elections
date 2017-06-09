from django.contrib import admin
from elections.models import *
from django.forms.models import BaseInlineFormSet


class ElectionsAdminSite(admin.AdminSite):
    site_header = "Elections 2000"


class CircuitInline(admin.TabularInline):
    model = CandidateResult
    can_delete = True
    extra = 0


class VoivodeshipAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']


class PrecinctAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'number']


class BoroughAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']


class ResultForm(BaseInlineFormSet):

    def clean(self):
        if any(self.errors):
            return

        sum_votes = 0
        for f in self.forms:
            if 'votes' not in f.cleaned_data:
                continue
            if f.cleaned_data['votes'] < 0:
                raise ValidationError("Number of votes is negative.")
            sum_votes += f.cleaned_data['votes']

        if sum_votes > self.instance.cards:
            raise ValidationError("Number of given cards is exceeded.")

        self.instance.valid_cards = sum_votes
        self.instance.save()


class ResultInline(admin.TabularInline):
    model = CandidateResult
    formset = ResultForm
    can_delete = False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request):
        return False


class CircuitAdmin(admin.ModelAdmin):
    search_fields = ['address', 'borough__name']
    list_display = ['address', 'get_borough']
    readonly_fields = ['valid_cards']
    inlines = [ResultInline]

    def get_borough(self, obj):
        return obj.borough.name

    get_borough.short_description = 'Borough'
    get_borough.admin_order_field = 'borough__name'


class CandidateAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']
    list_display = ['last_name', 'first_name']
    fields = ['first_name', 'last_name']


admin_site = ElectionsAdminSite(name='electionsadmin')
admin_site.register(Voivodeship, VoivodeshipAdmin)
admin_site.register(Borough, BoroughAdmin)
admin_site.register(Candidate, CandidateAdmin)
admin_site.register(Circuit, CircuitAdmin)
admin_site.register(Precinct, PrecinctAdmin)
