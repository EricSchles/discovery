from django.test import TestCase
from vendors.models import Vendors
from django.core.management import call_command

class VendorsLoadTest(TestCase):
    """Tests that the load_Vendors management command works and loads all the correct fields"""
    fixtures = ['naics.json', 'setasides.json', 'pools.json']

    def test_load(self):
        call_command('load_Vendors')

    
    def test_sam_expiration_not_null(self):
        null_Vendors = Vendors.objects.filter(sam_expiration_date=None).count()
        self.assertEqual(null_Vendors, 0)


    def test_pm_not_null(self):
        null_Vendors = Vendors.objects.filter(pm_email=None).count()
        self.assertEqual(null_Vendors, 0)

