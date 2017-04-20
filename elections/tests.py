from django.test import TestCase
from elections.forms import CircuitForm
from elections.models import Circuit, Borough, Candidate, CandidateResult
from django.test import Client


class BoroughSearchTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_no_search(self):
        context = self.client.get('/borough/search').context
        self.assertFalse(context["searched"])
        self.assertNotIn("results", context)

    def test_search_1(self):
        Borough.objects.create(name="asdkuhfaksfasf", code=1)
        response = self.client.get('/borough/search', {'query': "hfaks"})
        # check if searching was executed
        self.assertTrue(response.context["searched"])
        # check if found borough from database
        self.assertEqual(len(response.context["results"]), 1)
        # check HTML code - results should be printed out somewhere
        if len(response.context["results"]):
            self.assertContains(response, "asdkuhfaksfasf")

    def test_search_many(self):
        Borough.objects.create(name="a", code=1)
        Borough.objects.create(name="aa", code=2)
        Borough.objects.create(name="aaa", code=3)
        Borough.objects.create(name="b", code=4)
        response = self.client.get('/borough/search', {'query': "a"})
        self.assertEqual(len(response.context["results"]), 3)


class CircuitFormTest(TestCase):
    def setUp(self):
        self.circuit = Circuit.objects.create(
            address="Planet: Poland",
            cards=1000,
            valid_cards=500,
            borough=Borough.objects.create(name='b', code=1)
        )

        self.candidates = []
        self.candidates.append(Candidate.objects.create(first_name='A', last_name='B'))
        self.candidates.append(Candidate.objects.create(first_name='C', last_name='D'))

        for candidate in self.candidates:
            CandidateResult.objects.create(
                candidate=candidate,
                circuit=self.circuit,
                votes=0
            )

    def test_valid(self):
        data = {
            str(self.candidates[0].id): 1,
            str(self.candidates[1].id): 1,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertTrue(form.is_valid())

    def test_valid_2(self):
        data = {
            str(self.candidates[0].id): 50,
            str(self.candidates[1].id): 90,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertTrue(form.is_valid())

    def test_valid_3(self):
        data = {
            str(self.candidates[0].id): 0,
            str(self.candidates[1].id): 0,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertTrue(form.is_valid())

    def test_valid_4(self):
        data = {
            str(self.candidates[0].id): 500,
            str(self.candidates[1].id): 0,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertTrue(form.is_valid())

    def test_too_much_votes(self):
        data = {
            str(self.candidates[0].id): 1000,
            str(self.candidates[1].id): 2000,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertFalse(form.is_valid())

    def test_too_much_votes_2(self):
        data = {
            str(self.candidates[0].id): 0,
            str(self.candidates[1].id): 10000,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertFalse(form.is_valid())

    def test_negative_votes(self):
        data = {
            str(self.candidates[0].id): 100,
            str(self.candidates[1].id): -1,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertFalse(form.is_valid())

    def test_negative_votes_2(self):
        data = {
            str(self.candidates[0].id): -2,
            str(self.candidates[1].id): -2,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertFalse(form.is_valid())
