from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import User, AssetSpecs

from api.tests import APIBaseTestCase
client = APIClient()


class AssetSpecsAPITest(APIBaseTestCase):
    """ Tests for the AssetCategory endpoint"""

    def setUp(self):
        super(AssetSpecsAPITest, self).setUp()
        self.token_admin = 'testtoken'
        self.admin = User.objects.create_superuser(
            email='testadmin@gmail.com', cohort=19,
            slack_handle='admin', password='admin123'
        )
        self.user = User.objects.create(
            email='test_user@site.com', cohort=10,
            slack_handle='@test_user', password='user12345'
        )
        self.asset_specs_url = reverse('asset-specs-list')
        self.asset_specs = AssetSpecs.objects.create(
            screen_size=15,
            year_of_manufacture=2017,
            processor_speed=3.0,
            processor_type="Intel core i7",
            memory=8,
            storage=512
        )

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_create_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin.email}
        data = {
            "year_of_manufacture": 2015,
            "processor_type": "Intel core i5",
            "screen_size": 13,
            "storage": 256,
            "memory": 8
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.status_code, 201)
        self.assertIn(data['storage'], response.data.values())

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_create_specs_with_missing_fields(self,
                                                        mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin.email}
        data = {
            "year_of_manufacture": 2016,
            "processor_type": "Intel core i3",
            "screen_size": 15,
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            data['processor_type'],
            response.data['processor_type'])

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_get_single_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin.email}
        response = client.get(
            f"{self.asset_specs_url}/{self.asset_specs.id}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['processor_type'],
            self.asset_specs.processor_type)

    @patch('api.authentication.auth.verify_id_token')
    def test_non_admin_cannot_create_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {
            "year_of_manufacture": 2015,
            "processor_type": "Intel core i5",
            "screen_size": 13,
            "storage": 256,
            "memory": 8
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_non_admin_cannot_get_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_specs_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_cannot_create_specs_with_invalid_fields(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {
            "year_of_manufacture": 2011,
            "processor_type": "Intel core i5",
            "screen_size": 12,
            "storage": 256,
            "memory": 8
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_update_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin.email}
        data = {
            "storage": 128,
            "memory": 32
        }
        response = client.put(
            f"{self.asset_specs_url}/{self.asset_specs.id}",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertIn('storage', response.data.keys())
        self.assertEqual(data['memory'], response.data['memory'])

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_specs_unique_validation(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin.email}
        data = {
            "year_of_manufacture": 2017,
            "processor_type": "Intel core i7",
            "screen_size": 15,
            "storage": 512,
            "memory": 8
        }
        response = client.post(
            f"{self.asset_specs_url}",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['non_field_errors'],
            ['Similar asset specification already exist'])
