from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.contrib.auth import get_user_model

from ..models import (
    Asset,
    AssetModelNumber,
    AssetStatus,
    AssetMake,
    AssetType,
    AssetSubCategory,
    AssetCategory
)

from core.tests import CoreBaseTestCase
User = get_user_model()


class AssetTypeModelTest(CoreBaseTestCase):
    """Tests for the Asset Model"""

    def setUp(self):
        super(AssetTypeModelTest, self).setUp()
        self.user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )
        asset_category = AssetCategory.objects.create(
            category_name="Computer")
        asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name="Electronics", asset_category=asset_category)
        asset_type = AssetType.objects.create(
            asset_type="Accessory", asset_sub_category=asset_sub_category)
        make_label = AssetMake.objects.create(
            make_label="Sades", asset_type=asset_type)
        self.test_assetmodel = AssetModelNumber(
            model_number="IMN50987", make_label=make_label)
        self.test_assetmodel.save()

        self.test_asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=self.test_assetmodel,
            assigned_to=self.user,
            purchase_date="2018-07-10"
        )
        self.test_asset.save()

        self.all_assets = Asset.objects.all()
        self.all_assetmodels = AssetModelNumber.objects.all()

    def test_add_new_asset(self):
        """Test add new asset"""
        self.assertEqual(self.all_assets.count(), 1)
        new_asset = Asset(asset_code="IC002",
                          serial_number="SN0045",
                          model_number=self.test_assetmodel,
                          assigned_to=self.user,
                          purchase_date="2018-07-10")
        new_asset.save()
        self.assertEqual(self.all_assets.count(), 2)

    def test_cannot_add_existing_serial_number(self):
        """Test cannot add an asset existing serial number"""
        self.assertEqual(self.all_assets.count(), 1)
        serial_number = "SN001"
        new_asset = Asset(serial_number, "SN001", purchase_date="2018-07-10")
        with self.assertRaises(ValidationError):
            new_asset.save()
        self.assertEqual(self.all_assets.count(), 1)

    def test_cannot_add_existing_asset_code(self):
        """Test cannot add an asset existing asset code"""
        self.assertEqual(self.all_assets.count(), 1)
        asset_code = "IC002"
        new_asset = Asset(asset_code, "SN001", purchase_date="2018-07-10")
        with self.assertRaises(ValidationError):
            new_asset.save()
        self.assertEqual(self.all_assets.count(), 1)

    def test_asset_without_code(self):
        """Test error when new asset lacks serial number and asset code"""
        self.assertEqual(self.all_assets.count(), 1)
        new_asset = Asset()
        with self.assertRaises(ValidationError):
            new_asset.save()
        self.assertEqual(self.all_assets.count(), 1)

    def test_edit_asset_type(self):
        """Test edit an asset in model"""
        get_asset = Asset.objects.get(asset_code="IC001")
        get_asset.asset_code = "IC003"
        get_asset.save()
        self.assertEqual(self.all_assets.count(), 1)
        get_asset = Asset.objects.get(asset_code="IC003")
        self.assertEqual(get_asset.asset_code, "IC003")

    def test_delete_asset_type(self):
        """Test delete an asset type in model"""
        self.assertEqual(self.all_assets.count(), 1)
        get_asset = Asset.objects.get(asset_code="IC001")
        statuses = AssetStatus.objects.filter(asset=get_asset)
        for status in statuses:
            status.delete()
        get_asset.delete()
        self.assertEqual(self.all_assets.count(), 0)

    def test_give_asset_model_number(self):
        """Test that an asset can be assigned a model number"""
        self.assertEqual(self.all_assets.count(), 1)
        self.assertEqual(self.all_assetmodels.count(), 1)
        get_assetmodel = AssetModelNumber.objects.get(model_number="IMN50987")
        get_asset = Asset.objects.get(asset_code="IC001")
        get_asset.model_number = get_assetmodel
        get_asset.save()
        self.assertEqual(str(get_asset.model_number), "IMN50987")

    def test_delete_assetmodel_cascades(self):
        """Test that the Asset is not deleted when model number is deleted"""
        self.assertEqual(self.all_assets.count(), 1)
        self.assertEqual(self.all_assetmodels.count(), 1)
        get_assetmodel = AssetModelNumber.objects.get(model_number="IMN50987")
        get_asset = Asset.objects.get(asset_code="IC001")
        get_asset.model_number = get_assetmodel
        get_asset.save()
        with self.assertRaises(ProtectedError):
            get_assetmodel.delete()
        self.assertEqual(self.all_assets.count(), 1)
        self.assertEqual(self.all_assetmodels.count(), 1)

    def test_asset_status_can_be_changed(self):
        asset = Asset.objects.get(asset_code="IC001")
        asset.status = "Allocated"

        self.assertIn("Allocated", asset.status)

    def test_asset_model_string_representation(self):
        self.assertEqual(str(self.test_asset), "IC001, SN001, IMN50987")

    def test_can_add_asset_without_assigned_to_field(self):
        new_asset = Asset(asset_code="IC0050",
                          serial_number="SN0055",
                          model_number=self.test_assetmodel,
                          purchase_date="2018-07-10")
        new_asset.save()
        self.assertIsNone(new_asset.assigned_to)

    def test_can_add_asset_without_purchase_date_field(self):
        new_asset = Asset(asset_code="IC0050",
                          serial_number="SN0055",
                          model_number=self.test_assetmodel)
        new_asset.save()
        self.assertIsNone(new_asset.purchase_date)

    def test_that_the_default_verification_status_on_asset_is_true(self):
        self.assertTrue(self.test_asset.verified)
