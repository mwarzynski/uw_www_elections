from django.db import IntegrityError
from django.http.response import Http404, HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.views import View
from django.shortcuts import render
import elections.models
from elections.forms import *
from django.db.models import Sum
from django.db import transaction


class MainView(View):
    @staticmethod
    def prepare_results(results):
        s = 0
        for r in results:
            s += r.votes
        for r in results:
            r.percentage = r.votes * 100 / s
        i = 1
        for r in results:
            r.index = i
            i += 1
        return results

    @staticmethod
    def get_circuit(circuit_id):
        try:
            return elections.models.Circuit.objects.get(id=circuit_id)
        except elections.models.CandidateResult.DoesNotExist:
            raise Http404("Given circuit not found.")


class Country(MainView):
    def get(self, request):
        data = {
            'country_mode': True,
            "title": "Wybory prezydenckie 2000"
        }

        results = elections.models.Candidate.objects.annotate(votes=Sum('candidateresult__votes')).order_by('-votes')
        data["people"] = self.prepare_results(results)
        data["voivodeships"] = elections.models.Voivodeship.objects.annotate(votes=Sum('precinct__boroughs__circuit__candidateresult__votes'))

        return render(request, "elections/index.html", context=data)


class Voivodeship(MainView):
    def get(self, request, voivodeship_id):
        data = {}

        vs = elections.models.Voivodeship.objects.filter(id=voivodeship_id)
        if len(vs) == 0:
            raise Http404("Voivodeship not found.")
        v = vs[0]
        data["title"] = "Województwo - " + v.name

        results = elections.models.Candidate.objects.filter(candidateresult__circuit__borough__precinct__voivodeship_id=v.id).annotate(votes=Sum('candidateresult__votes')).order_by('-votes')
        data["people"] = self.prepare_results(results)

        precincts = elections.models.Precinct.objects.filter(voivodeship_id=v.id)
        pages = []
        for p in precincts:
            pages.append({'link': 'precinct/' + str(p.id), 'name': p.name + " (" + str(p.id) + ")"})
        data["pages"] = pages

        return render(request, "elections/index.html", context=data)


class Precinct(MainView):
    def get(self, request, precinct_id):
        data = {}
        ps = elections.models.Precinct.objects.filter(id=precinct_id)
        if len(ps) == 0:
            raise Http404("Precinct not found.")
        precinct = ps[0]
        data["title"] = "Okręg - " + precinct.name

        results = elections.models.Candidate.objects.filter(candidateresult__circuit__borough__precinct=precinct.id).annotate(votes=Sum('candidateresult__votes')).order_by('-votes')
        data["people"] = self.prepare_results(results)

        boroughs = elections.models.Borough.objects.filter(precinct=precinct.id)
        pages = []
        for b in boroughs:
            pages.append({'link': 'borough/' + str(b.id), 'name': b.name})
        data["pages"] = pages

        return render(request, "elections/index.html", context=data)


class Borough(MainView):
    def get(self, request, borough_id):
        data = {
            "borough_mode": True
        }

        bs = elections.models.Borough.objects.filter(id=borough_id)
        if len(bs) == 0:
            raise Http404("Borough not found.")
        borough = bs[0]
        data["title"] = "Gmina - " + borough.name

        results = elections.models.Candidate.objects.filter(candidateresult__circuit__borough=borough.id).annotate(votes=Sum('candidateresult__votes')).order_by('-votes')
        data["people"] = self.prepare_results(results)

        candidates = elections.models.Candidate.objects.order_by("last_name")
        data["candidates"] = candidates

        circuits = elections.models.Circuit.objects.filter(borough=borough.id).order_by("id")
        cdata = []
        i = 1
        for circuit in circuits:
            candidates = elections.models.Candidate.objects.filter(candidateresult__circuit=circuit.id).annotate(votes=Sum('candidateresult__votes')).order_by('last_name')
            cdata.append({
                'i': i,
                'id': circuit.id,
                'address': circuit.address,
                'candidates': candidates
            })
            i += 1
        data['circuits'] = cdata

        return render(request, "elections/index.html", context=data)


class BoroughSearch(View):
    @staticmethod
    def get(request):
        data = {
            'title': 'Wyszukiwarka gmin.',
            'searched': False,
        }
        query_text = request.GET.get('query')
        if not query_text:
            return render(request, "manage/search.html", context=data)

        results = elections.models.Borough.objects.filter(name__icontains=query_text)
        data['searched'] = True
        data['query'] = query_text
        data['results'] = results

        return render(request, "manage/search.html", context=data)


class CircuitEdit(MainView):

    def generate_data(self, circuit_id):
        circuit = self.get_circuit(circuit_id)
        return {
            "title": "Edycja obwodu - " + str(circuit.address) + " (" + str(circuit.id) + ")",
            "circuit": circuit,
            'form': CircuitForm(circuit=circuit)
        }

    def get(self, request, circuit_id):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to='/login')
        return render(request, "manage/edit.html", context=self.generate_data(circuit_id))

    def post(self, request, circuit_id):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to='/login')

        try:
            with transaction.atomic():
                circuit = self.get_circuit(circuit_id)
                form = CircuitForm(request.POST, circuit=circuit)

                if not form.is_valid():
                    data = self.generate_data(circuit_id)
                    data["form"] = form
                    return render(request, "manage/edit.html", context=data)

                candidates = []
                valid_votes = 0
                for candidate_id, votes in form.cleaned_data.items():
                    try:
                        c = elections.models.CandidateResult.objects.get(candidate_id=candidate_id, circuit_id=circuit.id)
                    except elections.models.CandidateResult.DoesNotExist:
                        return HttpResponse("Given candidate not found.")
                    c.votes = votes
                    candidates.append(c)
                    valid_votes += votes

                for c in candidates:
                    c.save()
                circuit.valid_cards = valid_votes
                circuit.save()

                return HttpResponseRedirect('/borough/' + str(circuit.borough_id))

        except IntegrityError:
            return HttpResponseServerError("Integrity error. Please redo your changes.")
