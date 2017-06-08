from django.contrib import admin


class ResultAdmins(admin.ModelAdmin):

    list_filter = ()
    search_fields = []
    list_display = []


# custom.admin.register(Voivodeship, VoivodeshipAdmin)
# custom.admin.register(Borough, BoroughAdmin)
# custom.admin.register(Candidate, CandidateAdmin)
# custom.admin.register(Circuit, CircuitAdmin)
# custom.admin.register(Precinct, PrecinctAdmin)
