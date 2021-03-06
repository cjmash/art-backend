from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import (
    Asset,
    AssetModelNumber,
    AssetStatus,
    AllocationHistory,
    AssetMake,
    AssetType,
    AssetSubCategory,
    AssetCategory
)

from core.tests import CoreBaseTestCase
User = get_user_model()
client = APIClient()


class AssetStatusModelTest(CoreBaseTestCase):
    """Tests for the Asset Status Model"""

    def setUp(self):
        super(AssetStatusModelTest, self).setUp()
        asset_category = AssetCategory.objects.create(
            category_name="Computer")
        asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name="Electronics", asset_category=asset_category)
        asset_type = AssetType.objects.create(
            asset_type="Accessory", asset_sub_category=asset_sub_category)
        make_label = AssetMake.objects.create(
            make_label="Sades", asset_type=asset_type)
        self.test_assetmodel1 = AssetModelNumber(
            model_number="IMN50987", make_label=make_label)
        self.test_assetmodel2 = AssetModelNumber(
            model_number="IMN50986", make_label=make_label)
        self.test_assetmodel1.save()
        self.test_assetmodel2.save()

        self.normal_user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )

        self.test_asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=self.test_assetmodel1,
            assigned_to=self.normal_user,
            purchase_date="2018-07-10",
        )
        self.test_asset.save()
        self.asset = Asset.objects.get(asset_code="IC001")
        self.asset_status = AssetStatus.objects.get(asset=self.asset)

    def test_create_asset_creates_new_status(self):
        """Tests that creating a new asset creates a new asset status log"""
        self.assertEqual(AssetStatus.objects.all().count(), 1)
        self.assertEqual(Asset.objects.all().count(), 1)
        test_asset2 = Asset(
            asset_code="IC002",
            serial_number="SN002",
            model_number=self.test_assetmodel2,
            assigned_to=self.normal_user,
            purchase_date="2018-07-10",
        )
        test_asset2.save()
        self.assertEqual(AssetStatus.objects.all().count(), 2)
        self.assertEqual(Asset.objects.all().count(), 2)

    def test_create_asset_status(self):
        """
        Tests that:
        - creating a new asset status of the same asset,
        - changing an assets current status saves the previous current status
        as the new previous status
        """
        self.assertEqual(AssetStatus.objects.all().count(), 1)
        asset_status = AssetStatus(
            asset=self.asset,
            current_status="Damaged")
        asset_status.save()
        new_asset_status = AssetStatus.objects.filter(asset=self.asset).\
            latest('created_at')
        self.assertEqual(new_asset_status.previous_status, "Available")
        self.assertEqual(new_asset_status.current_status, "Damaged")
        self.assertEqual(AssetStatus.objects.all().count(), 2)

    def test_default_status_is_available(self):
        """
        Tests that a new asset gets a 'Available' as default current status
        """
        model_count = AssetStatus.objects.all().count()
        self.assertEqual(self.asset_status.current_status, "Available")
        self.assertEqual(self.asset_status.previous_status, None)
        self.assertEqual(model_count, 1)

    def test_status_validation(self):
        """Test that status has to be in list of choices"""
        model_count = AssetStatus.objects.all().count()
        self.assertEqual(model_count, 1)
        asset_status = AssetStatus(
            asset=self.asset,
            current_status="Unused")
        with self.assertRaises(ValidationError):
            asset_status.save()
        new_asset_status = AssetStatus.objects.filter(asset=self.asset).\
            latest('created_at')
        self.assertEqual(new_asset_status.current_status, "Available")
        self.assertEqual(new_asset_status.previous_status, None)
        self.assertEqual(model_count, 1)

    def test_change_assigned_to_none(self):

        allocation_history = AllocationHistory(
            asset=self.test_asset,
            current_owner=self.normal_user
        )

        asset_status = AssetStatus(
            asset=self.test_asset,
            current_status="Allocated")

        allocation_history.save()
        asset_status.save()
        test_owner = str(self.test_asset.assigned_to)

        asset_status.current_status = "Available"
        asset_status.save()

        new_history = AllocationHistory.objects.filter(
            asset=self.test_asset).latest('created_at')

        self.assertIn(test_owner, 'test@site.com')
        self.assertIsNone(self.test_asset.assigned_to)
        self.assertIsNone(new_history.current_owner)
        self.assertIn(str(new_history.previous_owner), 'test@site.com')
