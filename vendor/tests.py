from django.test import TestCase
from vendor.models import Vendor
from django.core.management import call_command

class VendorLoadTest(TestCase):
    """Tests that the load_vendors management command works and loads all the correct fields"""
    fixtures = ['naics.json', 'setasides.json', 'pools.json']

    def test_load(self):
        call_command('load_vendors')

    
    def test_sam_expiration_not_null(self):
        null_vendors = Vendor.objects.filter(sam_expiration_date=None).count()
        self.assertEqual(null_vendors, 0)


    def test_pm_not_null(self):
        null_vendors = Vendor.objects.filter(pm_email=None).count()
        self.assertEqual(null_vendors, 0)

