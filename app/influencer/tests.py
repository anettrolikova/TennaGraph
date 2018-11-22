# Stdlib
from decimal import Decimal

# Pip imports
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

# App imports
from .services import HiveOne
from .models import Influencer
from .tasks import fetch_influencers_from_hive_one


class HiveOneServiceTestCase(APITestCase):

    ho = None

    def setUp(self):
        self.ho = HiveOne()

    def test_should_load_influencers(self):
        influencers = self.ho.load_influencers()

        self.assertTrue(isinstance(influencers, list))
        self.assertGreater(len(influencers), 0)

        # should be the instance of Influencer class
        influencer = influencers[0]
        self.assertTrue(isinstance(influencer, Influencer))

        # should save to db
        self.assertEqual(Influencer.objects.exists(), False)
        influencer.save()
        self.assertEqual(Influencer.objects.exists(), True)

    def test_should_fetch_influencers_from_hive_one(self):
        self.assertEqual(Influencer.objects.count(), 0)

        # load and store influencers
        fetch_influencers_from_hive_one()

        self.assertEqual(Influencer.objects.count(), 300)


class EIPsClientAPITestCase(APITestCase):

    def test_should_return_empty_list_of_influencers(self):
        url = reverse("influencer:influencer")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_should_return_list_of_eips(self):
        influencer_dict = {
            'twitter_id':       '12345',
            'score':            Decimal('123.452435400000000000'),
            'name':             'The best influencer on myself =)',
            'screen_name':      'malkevych',
            'friends_count':    124987,
            'followers_count':  3456,
        }
        Influencer.objects.create(**influencer_dict)

        url = reverse("influencer:influencer")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        eip_response = response.data[0]

        self.assertEqual(eip_response['twitter_id'],        influencer_dict['twitter_id'])
        self.assertEqual(Decimal(eip_response['score']),    influencer_dict['score'])
        self.assertEqual(eip_response['name'],              influencer_dict['name'])
        self.assertEqual(eip_response['screen_name'],       influencer_dict['screen_name'])
        self.assertEqual(eip_response['friends_count'],     influencer_dict['friends_count'])
        self.assertEqual(eip_response['followers_count'],   influencer_dict['followers_count'])