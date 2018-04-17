from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ..models import Item, ItemModelNumber, SecurityUser, AssetLog

User = get_user_model()
client = APIClient()


class ItemTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_user = 'testtoken'
        self.other_user = User.objects.create_user(
            email='user1@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_other_user = 'otherusertesttoken'
        itemmodel = ItemModelNumber(model_number="IMN50987")
        itemmodel.save()
        item = Item(
            item_code="IC001",
            serial_number="SN001",
            assigned_to=self.user,
            model_number=itemmodel,
            allocation_status="Allocated"
        )
        item.save()
        self.checked_by = SecurityUser.objects.create(
            email="sectest1@andela.com",
            password="devpassword",
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="254720900900",
            badge_number="AE23"
        )
        self.item = item
        self.items_url = reverse('items-list')

    def test_non_authenticated_user_view_items(self):
        response = client.get(self.items_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_non_owner_view_items(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        response = client.get(
            self.items_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user))
        self.assertEqual(response.data, [])
        self.assertEqual(len(response.data), Item.objects.count() - 1)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_owner_view_items(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            self.items_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.item.item_code, response.data[0].values())
        self.assertEqual(len(response.data), Item.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_owner_view_single_item(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            "{}{}/".format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.item.item_code, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_items_api_endpoint_cant_allow_post(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.post(
            self.items_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.data, {
            'detail': 'Method "POST" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_items_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.put(
            '{}{}/'.format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_items_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.patch(
            '{}{}/'.format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_items_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.delete(
            '{}{}/'.format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_items_detail_api_endpoint_contain_assigned_to_details(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.user.email,
                      response.data['assigned_to'].values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_items_assigned_to_details_has_no_password(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertNotIn('password', response.data['assigned_to'].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_non_checked_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'], None)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_checked_in_asset(
            self, mock_verify_id_token):
        AssetLog.objects.create(
            checked_by=self.checked_by,
            asset=self.item,
            log_type="Checkin"
        )

        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'],
                         "checked_in")
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_checkout_in_asset(
            self, mock_verify_id_token):
        AssetLog.objects.create(
            checked_by=self.checked_by,
            asset=self.item,
            log_type="Checkout"
        )
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.items_url, self.item.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'],
                         "checked_out")
        self.assertEqual(response.status_code, 200)