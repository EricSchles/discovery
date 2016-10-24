import logging
import time
import traceback
import sys
import warnings

import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from vendor.models import Vendor, Pool, SetAside, SamLoad

warnings.filterwarnings('ignore')

class Command(BaseCommand):
    """
    Loops through each vendor in database and adds SAM information to its record
    """

    logger = logging.getLogger('sam')

    def get_value(self, obj, key, vendor):
        try:
            return obj[key]
        except KeyError as k:
            self.logger.debug("There was a key error on {0}: {1}".format(vendor.duns, k))
            return None

    def handle(self, *args, **kwargs):

        print("-------BEGIN CHECK_SAM PROCESS-------")
        try:
            vendors = Vendor.objects.all()
            for v in vendors:
                #keep from bringing the SAM API down
                time.sleep(2)
                #get SAM.gov API response for this vendor
                uri = settings.SAM_API_URL + v.duns_4 + '?api_key=' + settings.SAM_API_KEY
                log_uri = settings.SAM_API_URL + v.duns_4

                self.logger.debug("Fetching vendor at {0}".format(log_uri))
                req = requests.get(uri)
                
                #check and see if error code is forbidden -- exit because api key problem
                if req.status_code==403:
                    if 'Message' in req.json():
                        self.logger.debug("There was a 403 error on {0}. Registration information forbidden".format(log_uri))
                    else:
                        raise Exception('Data.gov API key is invalid')
                try:
                    sam_data = req.json()
                except ValueError:
                    #the api did not return anything. Sleep and try again
                    time.sleep(5)
                    sam_data = req.json()

                if 'sam_data' in sam_data:
                    if 'registration' in sam_data['sam_data']:
                        reg = sam_data['sam_data']['registration']
                        v.sam_status = self.get_value(reg, 'status', v)
                        v.sam_activation_date = self.get_value(reg, 'activationDate', v)
                        v.sam_expiration_date = self.get_value(reg, 'expirationDate', v)
                        v.sam_exclusion = self.get_value(reg, 'hasKnownExclusion', v)
                        v.cage = self.get_value(reg, 'cage', v)
                        addr = self.get_value(reg, 'samAddress', v)
                        if addr:
                            v.sam_address = self.get_value(addr, 'Line1', v)
                            v.sam_citystate = "{0}, {1} {2}".format(self.get_value(addr, 'City', v), 
                                                                      self.get_value(addr, 'stateorProvince', v), 
                                                                      self.get_value(addr, 'Zip', v))
                    
                        v.sam_url = self.get_value(reg, 'corporateUrl', v)
                        if v.sam_url and v.sam_url[:3].lower() == "www" : 
                            v.sam_url = 'http://' + v.sam_url

                        setasides = self.get_value(reg, 'businessTypes', v)
                        for code in setasides:
                            try:
                                sa = SetAside.objects.get(code__iexact=code)
                                if sa not in v.setasides.all():
                                    v.setasides.add(sa)

                            except SetAside.DoesNotExist:
                                continue
                        v.save()
                        
                    else:
                        self.logger.debug("'registration' key is missing for {}".format(log_uri))

                elif 'Error' in sam_data:
                    self.logger.debug("SAM API returned an error for {0}, and duns {1}".format(log_uri, v.duns ))
                else:
                    self.logger.debug("Could not load data from {} for unknown reason".format(log_uri))

            sam_load = SamLoad(sam_load=timezone.now())
            sam_load.save()
        
        except Exception as e:
            print("MAJOR ERROR -- PROCESS ENDING EXCEPTION --  {0}".format(e))
            print (traceback.format_exc())
            self.logger.debug("MAJOR ERROR -- PROCESS ENDING EXCEPTION -- {0}".format(e))
        
        print("-------END CHECK_SAM PROCESS-------")


