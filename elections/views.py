from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from django.db.models import Sum

from elections.forms import CircuitForm
import elections.models

from rest_framework.views import APIView


class UTFJSONRenderer(JSONRenderer):
    charset = 'utf-8'


class MainView(APIView):
    renderer_classes = (UTFJSONRenderer,)

    @staticmethod
    def prepare_people(candidates):
        cd = []
        s = 0
        for c in candidates:
            s += c.votes
        for c in candidates:
            c.percentage = round(c.votes * 100 / s, 2)

        for c in candidates:
            cd.append({
                "name": c.__str__(),
                "votes": c.votes,
                "percentage": c.percentage
            })
        return cd


class ResultsCountry(MainView):
    def get(self, request):
        return Response({
            "people": self.prepare_people(elections.models.Candidate.objects.annotate(votes=Sum('candidateresult__votes')).order_by('-votes'))
        })


class ResultsVoivodeship(MainView):
    def get(self, request, voivodeship_id):
        v = elections.models.Voivodeship.objects.filter(id=voivodeship_id)
        if not v:
            return Response({'message': "Voivodeship not found."}, status=404)
        v = v.first()
        return Response({
            "name": v.name,
            "people": self.prepare_people(elections.models.Candidate.objects.filter(candidateresult__circuit__borough__precinct__voivodeship=v.id).annotate(
                votes=Sum('candidateresult__votes')).order_by('-votes'))
        })


class ResultsPrecinct(MainView):
    def get(self, request, precinct_id):
        precinct = elections.models.Precinct.objects.filter(id=precinct_id)
        if not precinct:
            return Response({'message': "Precinct not found."}, status=404)
        precinct = precinct.first()
        return Response({
            "name": precinct.name,
            "people": self.prepare_people(elections.models.Candidate.objects.filter(candidateresult__circuit__borough__precinct=precinct.id).annotate(
                votes=Sum('candidateresult__votes')).order_by('-votes'))
        })


class ResultsBorough(MainView):
    def get(self, request, borough_id):
        borough = elections.models.Borough.objects.filter(id=borough_id)
        if not borough:
            return Response({'message': "Borough not found."}, status=404)
        borough = borough.first()
        return Response({
            "name": borough.name,
            "people": self.prepare_people(elections.models.Candidate.objects.filter(candidateresult__circuit__borough=borough.id).annotate(
                votes=Sum('candidateresult__votes')).order_by('-votes'))
        })


class ResultsCircuit(MainView):
    def get(self, request, borough_id):
        borough = elections.models.Borough.objects.filter(id=borough_id)
        if not borough:
            return Response({'message': "Borough not found."}, status=404)
        borough = borough.first()

        results = []
        for circuit in elections.models.Circuit.objects.filter(borough=borough.id).order_by("id"):
            candidates = elections.models.Candidate.objects.filter(candidateresult__circuit=circuit.id).annotate(votes=Sum('candidateresult__votes')).order_by(
                'last_name')
            results.append({
                'id': circuit.id,
                'address': circuit.address,
                'votes': [c.votes for c in candidates]
            })
        return Response({
            "candidates": [str(c) for c in elections.models.Candidate.objects.order_by("last_name")],
            "circuits": results
        })


class PagesVoivodeship(MainView):
    def get(self, request, voivodeship_id):
        v = elections.models.Voivodeship.objects.filter(id=voivodeship_id)
        if not v:
            return Response({'message': "Voivodeship not found."}, status=404)
        v = v.first()
        data = {}
        precincts = elections.models.Precinct.objects.filter(voivodeship_id=v.id)
        data["pages"] = [{'link': 'precinct/' + str(p.id), 'name': p.name + " (" + str(p.id) + ")"} for p in precincts]
        return Response(data)


class PagesPrecinct(MainView):
    def get(self, request, precinct_id):
        precinct = elections.models.Precinct.objects.filter(id=precinct_id)
        if not precinct:
            return Response({'message': "Precinct not found."}, status=404)
        precinct = precinct.first()
        data = {}
        boroughs = elections.models.Borough.objects.filter(precinct=precinct.id)
        pages = [{'link': 'borough/' + str(b.id), 'name': b.name} for b in boroughs]
        data["pages"] = pages
        return Response(data)


class Voivodeship(MainView):
    def get(self, request):
        return Response({"voivodeships": [{"id": v.id, "name": v.name, "code": v.code, "votes": v.votes} for v in
                                              elections.models.Voivodeship.objects.annotate(
                                                  votes=Sum('precinct__boroughs__circuit__candidateresult__votes'))], })


class SearchBorough(MainView):
    @staticmethod
    def get(request):
        query = request.GET.get('query')
        if not query:
            return Response({"message": "Query is not defined."}, status=400)
        boroughs = elections.models.Borough.objects.filter(name__icontains=query)
        results = [{'id': b.id, 'name': b.name, 'code': b.code} for b in boroughs]
        return Response({
            "data": results
        })


class EditCircuit(MainView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, circuit_id):
        c = elections.models.Circuit.objects.filter(id=circuit_id)
        if not c:
            return Response({'message': "Circuit not found."}, status=404)
        circuit = c.first()
        data = {}
        results = circuit.candidateresult_set.all()
        fields = []
        for result in results:
            fields.append({
                    'id': result.candidate.id,
                    'candidate': result.candidate.__str__(),
                    'votes': result.votes,
                })
        data['results'] = fields
        data['name'] = circuit.address
        data['all_votes'] = circuit.cards
        return Response(data)

    def post(self, request, circuit_id):
        if 'results' not in request.data:
            return Response({'message': 'No results in data.'}, status=400)

        try:
            with transaction.atomic():
                # Get circuit
                circuit = elections.models.Circuit.objects.select_for_update().filter(id=circuit_id)
                if not circuit:
                    return Response({'message': "Circuit not found."}, status=404)
                circuit = circuit.first()

                # Check if data is valid
                valid_votes = 0
                candidates = []
                for result in request.data['results']:
                    if 'id' not in result:
                        return Response({'message': "Invalid result item. No ID."}, status=400)
                    c = elections.models.CandidateResult.objects.get(candidate_id=result['id'], circuit_id=circuit.id)
                    if not c:
                        return Response({"message": "Given with ID=" + str(result['id']) + " not found."}, status=404)

                    if result['votes'] < 0:
                        return Response({'message': 'Cannot set negative votes.'}, status=400)

                    try:
                        v = int(result['votes'])
                    except:
                        return Response({"message": "Number of votes is not integer."}, status=400)

                    if result['votes'] != v:
                        return Response({"message": "Number of votes is not integer."}, status=400)

                    # Update retrieved candidate object.
                    c.votes = result['votes']
                    candidates.append(c)
                    valid_votes += result['votes']

                if circuit.cards < valid_votes:
                    return Response({"message": 'Number of valid votes is higher than all votes.'}, status=400)

                # Save data to database.
                circuit.valid_cards = valid_votes
                circuit.save()
                for c in candidates:
                    c.save()

                return Response(status=204)

        except IntegrityError:
            return Response({"message": "Integrity error. Please redo your changes."}, status=500)
