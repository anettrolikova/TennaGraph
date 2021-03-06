# Stdlib imports
from decimal import Decimal

# Django imports
from django.conf import settings

# Pip imports
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

# Project imports
from eip.models import EIP
from influencer.models import Influencer
from github_client.services import GitHubDB

# App imports
from .models import Stance
from .tasks import check_availability_proofs_of_stances



class StancesClientAPITestCase(APITestCase):

    eip = None
    eip2 = None
    gh = None

    def setUp(self):
        eip_dict = {
            'eip_num': '12',
            'eip_title': 'Title of EIP',
            'eip_status': EIP.ACTIVE,
            'eip_type': EIP.INFORMATIONAL,
            'eip_category': EIP.ERC,
            'eip_authors': 'Authors here',
            'eip_created': '1994-12-23',

            'file_name': 'File name here',
            'file_download_url': 'https://google.com.ua/',
            'file_content': 'Here markdown text from md file',
            'file_sha': '0xjsfidsfseuiui34893hbsfo2i2ifeg',
        }
        eip2_dict = {
            'eip_num': '8',
            'eip_title': 'Title of EIP 2',
            'eip_status': EIP.ACTIVE,
            'eip_type': EIP.INFORMATIONAL,
            'eip_category': EIP.ERC,
            'eip_authors': 'Authors here 2',
            'eip_created': '1994-02-06',

            'file_name': 'File name here 2',
            'file_download_url': 'https://google.com.ua/2/',
            'file_content': 'Here markdown text from md file 2',
            'file_sha': '0xjsfidsfseuiui34893hbsfo2i2ifeg2',
        }
        influencer = {
            'twitter_id':       '12345',
            'score':            Decimal('123.452435400000000000'),
            'name':             'The best influencer on myself =)',
            'screen_name':      'malkevych',
            'following_count':    124987,
            'followers_count':  3456,
        }
        self.eip = EIP.objects.create(**eip_dict)
        self.eip2 = EIP.objects.create(**eip2_dict)
        self.influencer = Influencer.objects.create(**influencer)
        self.gh = GitHubDB()

        # Clear repo before run tests
        self.gh.delete_repo_content()

    def test_should_return_empty_list_of_stances(self):
        url = reverse("stance:stance")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_should_return_list_of_stances(self):
        stance_dict = {
            'author': 'malkevych',
            'author_from_social': Stance.TWITTER,
            'proof_url': 'https://google.com',
            'choice': Stance.YAY,
            'eip': self.eip
        }
        Stance.objects.create(**stance_dict)

        url = reverse("stance:stance")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


        stance_response = response.data[0]

        self.assertEqual(stance_response['author'],         'malkevych')
        self.assertEqual(stance_response['proof_url'],      stance_dict['proof_url'])
        self.assertEqual(stance_response['choice']['key'],  stance_dict['choice'])
        self.assertEqual(stance_response['status']['key'],  'PENDING')


    def test_should_retrieve_the_stance(self):
        stance_dict = {
            'author': 'malkevych',
            'author_from_social': Stance.TWITTER,
            'proof_url': 'https://google.com',
            'choice': Stance.YAY,
            'eip': self.eip
        }
        stance = Stance.objects.create(**stance_dict)

        url = reverse("stance:stance_retrieve", kwargs={'pk': stance.id})

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, dict))

        stance_response = response.data

        self.assertEqual(stance_response['author'],         'malkevych')
        self.assertEqual(stance_response['proof_url'],      stance_dict['proof_url'])
        self.assertEqual(stance_response['choice']['key'],  stance_dict['choice'])
        self.assertEqual(stance_response['status']['key'],  'PENDING')

    def test_should_retrieve_the_stances_of_eip(self):
        stance_dict = {
            'author': 'malkevych',
            'author_from_social': Stance.TWITTER,
            'proof_url': 'https://google.com',
            'choice': Stance.YAY,
            'eip': self.eip
        }
        stance2_dict = {
            'author': 'malkevych2',
            'author_from_social': Stance.TWITTER,
            'proof_url': 'https://google.com/2/',
            'choice': Stance.NAY,
            'eip': self.eip2
        }
        Stance.objects.create(**stance_dict)
        Stance.objects.create(**stance2_dict)

        url = reverse("stance:stance")

        url = url + '?eip_num={}'.format(self.eip.eip_num)

        response = self.client.get(url, format='json')


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

        stance_response = response.data
        self.assertEqual(len(stance_response), 1)

        stance = stance_response[0]
        self.assertEqual(stance['author'],         'malkevych')
        self.assertEqual(stance['proof_url'],      stance_dict['proof_url'])
        self.assertEqual(stance['choice']['key'],  stance_dict['choice'])
        self.assertEqual(stance['status']['key'],  'PENDING')

    def test_should_create_new_stance(self):
        stance_dict = {
            'author': '@malkevych',
            'author_from_social': Stance.TWITTER,
            'proof_url': 'https://google.com',
            'choice': Stance.YAY,
            'eip_num': self.eip.eip_num,
        }

        url = reverse("stance:stance")
        response = self.client.post(url, data=stance_dict, format='json')

        # print("RESPONSE: {}".format(response.data))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(isinstance(response.data, dict))

        stance_response = response.data

        self.assertEqual(stance_response['author'], 'malkevych')
        self.assertEqual(stance_response['proof_url'], stance_dict['proof_url'])
        self.assertEqual(stance_response['choice']['key'], stance_dict['choice'])
        self.assertEqual(stance_response['status']['key'], 'PENDING')

        # should exists on github repo
        stance = Stance.objects.get(id=stance_response['id'])
        is_exists = self.gh.is_model_exists(stance)
        self.assertTrue(is_exists)

    def test_should_raise_git_hub_error(self):
        correct_git_hub_pass = settings.GITHUB_PASSWORD
        settings.GITHUB_PASSWORD = 'not right pass'
        stance_dict = {
            'author': '@malkevych',
            'author_from_social': Stance.TWITTER,
            'proof_url': 'https://google.com',
            'choice': Stance.YAY,
            'eip_num': self.eip.eip_num,
        }

        url = reverse("stance:stance")
        response = self.client.post(url, data=stance_dict, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # set back right password
        settings.GITHUB_PASSWORD = correct_git_hub_pass

    def test_should_create_new_stance_with_influencer(self):
        stance_dict = {
            'author': '@maLkEvyCh',
            'author_from_social': Stance.TWITTER,
            'proof_url': 'https://google.com',
            'choice': Stance.YAY,
            'eip_num': self.eip.eip_num,
        }

        url = reverse("stance:stance")
        response = self.client.post(url, data=stance_dict, format='json')

        # print("RESPONSE: {}".format(response.data))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(isinstance(response.data, dict))

        stance_response = response.data

        self.assertEqual(stance_response['author'],                     'maLkEvyCh')
        self.assertEqual(stance_response['influencer']['screen_name'],  self.influencer.screen_name)
        self.assertEqual(stance_response['proof_url'],                  stance_dict['proof_url'])
        self.assertEqual(stance_response['choice']['key'],              stance_dict['choice'])
        self.assertEqual(stance_response['status']['key'],              'PENDING')

        # should exists on github repo
        stance = Stance.objects.get(id=stance_response['id'])
        is_exists = self.gh.is_model_exists(stance)
        self.assertTrue(is_exists)

    def test_should_delete_stance_if_twitter_status_is_not_exist(self):
        self.assertFalse(Stance.objects.exists())

        stance_dict = {
            'author': '@maLkEvyCh',
            'author_from_social': Stance.TWITTER,
            'proof_url': 'https://twitter.com/bomalkevych/status/1077261352585043969',
            'choice': Stance.YAY,
            'eip_num': self.eip.eip_num,
        }

        url = reverse("stance:stance")
        response = self.client.post(url, data=stance_dict, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Stance.objects.exists())

        check_availability_proofs_of_stances()

        self.assertFalse(Stance.objects.exists())



