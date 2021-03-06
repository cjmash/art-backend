import sys
import os
import csv
from tqdm import tqdm
import django

from utils.helpers import (display_inserted, display_skipped,
                           write_record_skipped)

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
file_path = sys.path[-1]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from core.models.asset import (
    AssetType,
    AssetMake,
    Asset,
    AssetModelNumber,
    AssetCategory,
    AssetSubCategory,
) # noqa

rows = []
out = []


def post_asset_make(f, file_length): # noqa
    """
    Bulk creates asset make
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            row['count'] = counter
            make_label_value = row.get('Make', '').strip() or None
            asset_type_value = row.get('Type', '').strip() or None
            if not make_label_value:
                reason = 'asset make has no value'
                row['Reasons'] = reason
                skipped['make_{}'.format(counter)] = [(reason), counter]
                row_check(row)

            elif not asset_type_value:
                reason = 'asset type has no value'
                row['Reasons'] = reason
                skipped['type_{}'.format(counter)] = [(reason), counter]
                row_check(row)

            else:
                asset_make = AssetMake.objects.\
                    filter(make_label=make_label_value)\
                    .exists()
                asset_type = AssetType.objects.filter(
                    asset_type=asset_type_value).exists()

                if asset_make:
                    reason = 'asset_make {0} already exists'.format(
                        make_label_value)
                    skipped[make_label_value] = [(reason), counter]
                elif not asset_type:
                    reason = 'asset type {0} does not exist'.format(
                        asset_type_value)
                    row['Reasons'] = reason
                    skipped[asset_type_value] = [(reason), counter]
                    row_check(row)
                else:
                    asset_type = AssetType.objects.filter(
                        asset_type=asset_type_value).first()
                    new_asset_make = AssetMake.objects.\
                        create(make_label=make_label_value,
                               asset_type=asset_type)

                    try:
                        new_asset_make.save()
                        inserted_records.append([new_asset_make, counter])
                    except Exception as e:
                        reason = 'unable to save asset type {}: {}'.format(
                            asset_type_value, e)
                        row['Reasons'] = reason
                        skipped[asset_type_value] = [(reason), counter]
                        row_check(row)
                counter += 1
            pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET MAKES")
    display_skipped(skipped)


def post_asset(f, file_length): # noqa
    """
    Bulk creates assets
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            row['count'] = counter
            model_number = row.get('Model Number', '').strip() or None
            asset_code = row.get('Asset Code', '').strip() or None
            serial_number = row.get('Serial No.', '').strip() or None

            if model_number and (asset_code or serial_number):
                existing_model_number = AssetModelNumber.objects.get(
                    model_number=model_number)
                asset_code_status = None
                serial_number_status = None
                if asset_code:
                    asset_code_status = Asset.objects.filter(
                        asset_code=asset_code).exists()
                if serial_number:
                    serial_number_status = Asset.objects.filter(
                        serial_number=serial_number).exists()
                if asset_code_status:
                    reason = 'asset_code {0} already exists.'.format(
                        asset_code)
                    row['Reasons'] = reason
                    skipped[asset_code] = [(reason), counter]
                    row_check(row)

                elif serial_number_status:
                    reason = 'serial_number {0} already exists.'.format(
                        serial_number)
                    row['Reasons'] = reason
                    skipped[serial_number] = [(reason), counter]
                    row_check(row)
                elif not existing_model_number:
                    reason = 'model number {0} does not exist'.format(
                        model_number)
                    row['Reasons'] = reason
                    skipped[model_number] = [(reason), counter]
                    row_check(row)
                else:
                    asset = Asset()
                    asset.asset_code = asset_code
                    asset.serial_number = serial_number
                    asset.model_number = existing_model_number
                    try:
                        asset.save()
                        inserted_records.append([asset, counter])
                    except Exception as e:
                        reason = 'unable to save asset {} {}: {}'.format(
                            asset_code, serial_number, e)
                        row['Reasons'] = reason
                        skipped['{}_{}'.format(
                            asset_code, serial_number)] = [(reason),
                                                           counter]
                        row_check(row)
            elif not (asset_code or serial_number):
                reason = 'asset must have either asset code or serial number'
                row['Reasons'] = reason
                skipped['{}_{}'.format(
                    asset_code, serial_number)] = [(reason), counter]
                row_check(row)
            else:
                reason = 'model number has no value'
                row['Reasons'] = reason
                skipped['model_{}'.format(counter)] = [(reason), counter]
                row_check(row)
            counter += 1
            pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSETS")
    display_skipped(skipped)
    write_record_skipped(out, file_path)
    # print(out)


def post_asset_category(f, file_length): # noqa
    """
    Bulk creates asset category
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            row['count'] = counter
            assets_category = row.get('Category', '').strip() or None

            if not assets_category:
                reason = 'category has no value'
                row['Reasons'] = reason
                skipped['cat_{}'.format(counter)] = [(reason), counter]
                row_check(row)
            else:
                assets_category_status = AssetCategory.objects. \
                    filter(category_name=assets_category).exists()
                if assets_category_status:
                    reason = 'Category {0} already exists'.format(
                        assets_category)
                    skipped[assets_category] = [(reason), counter]
                else:
                    new_asset_category = AssetCategory.objects.create(
                        category_name=assets_category)
                    try:
                        new_asset_category.save()
                        inserted_records.append([new_asset_category, counter])
                    except Exception as e:
                        reason = 'Unable to save category {}: {}'.format(
                            assets_category, e)
                        row['Reasons'] = reason
                        skipped[assets_category] = [(reason), counter]
                        row_check(row)

            counter += 1
            pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET CATEGORIES")
    display_skipped(skipped)


def post_asset_subcategory(f, file_length): # noqa
    """
    Bulk creates asset category
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            row['count'] = counter
            assets_category = row.get('Category', '').strip() or None
            assets_subcategory = row.get('Sub-Category', '').strip() or None
            if not assets_category:
                reason = 'category has no value'
                row['Reasons'] = reason
                skipped['cat_{}'.format(counter)] = [(reason), counter]
                row_check(row)
            elif not assets_subcategory:
                reason = 'sub-category has no value'
                row['Reasons'] = reason
                skipped['subcat_{}'.format(counter)] = [(reason), counter]
                row_check(row)

            else:
                category = AssetCategory.objects. \
                    filter(category_name=assets_category)
                assets_subcategory_status = AssetSubCategory.objects. \
                    filter(sub_category_name=assets_subcategory).exists()
                if assets_subcategory_status:
                    reason = 'Sub Category {0} already exists'.format(
                        assets_subcategory)
                    skipped[assets_subcategory] = [(reason), counter]
                elif not category.exists():
                    reason = 'category {0} does not exist'.format(
                        assets_category)
                    row['Reasons'] = reason
                    skipped[assets_category] = [(reason), counter]
                    row_check(row)
                else:
                    try:
                        new_subcategory = AssetSubCategory.objects.create(
                            sub_category_name=assets_subcategory,
                            asset_category=category)
                        new_subcategory.save()
                        inserted_records.append(
                            [new_subcategory, counter])
                    except Exception as e:
                        reason = 'Unable to save category {}: {}'.format(
                            assets_subcategory, e)
                        row['Reasons'] = reason
                        skipped[assets_category] = [(reason), counter]
            counter += 1
            pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET SUB-CATEGORIES")
    display_skipped(skipped)


def post_asset_model_no(f, file_length): # noqa
    """
    Bulk creates asset model number
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            row['count'] = counter
            asset_make = row.get('Make', '').strip() or None
            model_number = row.get('Model Number', '').strip() or None
            if not asset_make:
                reason = 'make has no value'
                row['Reasons'] = reason
                skipped['make_{}'.format(counter)] = [(reason), counter]
                row_check(row)
            elif not model_number:
                reason = 'model number has no value'
                row['Reasons'] = reason
                skipped['model_{}'.format(counter)] = [(reason), counter]
                row_check(row)
            else:
                asset_model_no = AssetModelNumber.objects.filter(
                    model_number=model_number).exists()
                existing_make = AssetMake.objects.get(make_label=asset_make)

                if asset_model_no:
                    reason = 'asset_model_no {0} already exists'.format(
                        model_number)
                    skipped[model_number] = [(reason), counter]
                elif not existing_make:
                    reason = 'asset make {0} does not exist'.format(
                        asset_make)
                    row['Reasons'] = reason
                    skipped[asset_make] = [(reason), counter]
                    row_check(row)

                else:
                    new_asset_model_no = AssetModelNumber()
                    new_asset_model_no.model_number = model_number
                    new_asset_model_no.make_label = existing_make
                    try:
                        new_asset_model_no.save()
                        inserted_records.append([new_asset_model_no, counter])
                    except Exception as e:
                        reason = 'Unable to save model no {}: {}'.format(
                            model_number, e)
                        row['Reasons'] = reason
                        skipped[model_number] = [(reason), counter]
                        row_check(row)
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET MODELS")
    display_skipped(skipped)


def post_asset_types(f, file_length): # noqa
    """
    Bulk creates asset types
    :param f: open csv file
    :param file_length: length of csv data
    :return:
    """
    f.seek(0)
    data = csv.DictReader(f, delimiter=',')
    skipped = dict()
    inserted_records = []
    counter = 1
    with tqdm(total=file_length) as pbar:
        for row in data:
            row['count'] = counter
            asset_type = row.get('Type', '').strip() or None
            sub_category = row.get('Sub-Category', '').strip() or None
            if not asset_type:
                reason = 'asset type has no value'
                row['Reasons'] = reason
                skipped['type_{}'.format(counter)] = [(reason), counter]
                row_check(row)
            elif not sub_category:
                reason = 'sub-category has no value'
                row['Reasons'] = reason
                skipped['subcat_{}'.format(counter)] = [(reason), counter]
                row_check(row)
            else:
                sub_category_name = AssetSubCategory.objects.get(
                    sub_category_name=sub_category)
                asset_type_status = AssetType.objects.filter(
                    asset_type=asset_type).exists()
                if not sub_category_name:
                    reason = 'Sub Category {0} does not exist'.format(
                        sub_category)
                    row['Reasons'] = reason
                    skipped[sub_category] = [(reason), counter]
                    row_check(row)
                elif asset_type_status:
                    reason = 'asset_type {0} already exists'.format(
                        asset_type)
                    skipped[asset_type] = [(reason), counter]
                else:
                    asset = AssetType()
                    asset.asset_type = asset_type
                    asset.asset_sub_category = sub_category_name
                    try:
                        asset.save()
                        inserted_records.append([asset, counter])
                    except Exception as e:
                        reason = 'Unable to save asset type {}: {}'.format(
                            asset_type, e)
                        row['Reasons'] = reason
                        skipped[asset_type] = [(reason), counter]
                        row_check(row)
                counter += 1
                pbar.update(1)
    print("\n")
    display_inserted(inserted_records, "ASSET TYPES")
    display_skipped(skipped)


def row_check(row):
    row['Reasons'] = set([row.pop('Reasons')])
    for line in out:
        if line.get('count') == row.get('count'):
            line['Reasons'] = line['Reasons'].union(row['Reasons'])
            return
    out.append(row)
