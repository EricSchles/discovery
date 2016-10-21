from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.core.management import call_command
from django.conf import settings
from pyfpds import Contracts
from vendors.models import Vendors
from contract.models import Contract, FPDSLoad
from contract import catch_key_error
from datetime import datetime, timedelta
import pytz
import logging
import traceback

def get_award_id_obj(award):
    print("got to get_award_id_obj")
    if 'awardID' in award: 
        return award['awardID']
    else:
        return award['OtherTransactionAwardID']['OtherTransactionAwardContractID']


def get_piid(award_id):
    print("got to get_piid")
    piid = ''
    if 'referencedIDVID' in award_id:
        #part of an IDIQ
        piid = award_id['referencedIDVID']['PIID'] + '_' 
    elif 'PIID' in award_id:
        return award_id['PIID']

    piid += award_id['awardContractID']['PIID']

    return piid

def get_mod(award_id):
    print("got to get_mod")
    if 'modNumber' in award_id:
        return award_id['modNumber']
    return award_id['awardContractID']['modNumber']

def get_agency_id(award_id):
    print("got to get_agency_id")
    if 'awardContractID' in award_id:
        return award_id['awardContractID']['agencyID']['#text']
    else:
        return award_id['agencyID']['#text']

def get_agency_name(award_id):
    print("got to get_agency_name")
    if 'awardContractID' in award_id:
        return award_id['awardContractID']['agencyID']['@name']
    else:
        return award_id['agencyID']['@name'] 

@catch_key_error
def get_transaction_number(award_id):
    print("got to get_transaction_number")
    try:
        return award_id['awardContractID']['transactionNumber']
    except:
        return None
    
@catch_key_error
def get_ultimate_completion_date(award):
    print("got to get_ultimate_completion_date")
    try:
        return award['relevantContractDates']['ultimateCompletionDate']
    except:
        return None
    
@catch_key_error
def get_current_completion_date(award):
    print("got to get_current_completion_date")
    try:
        return award['relevantContractDates']['currentCompletionDate']
    except:
        return None
    
@catch_key_error
def get_annual_revenue(award):
    print("got to get_annual_revenue")
    try:
        return award['vendor']['vendorSiteDetails']['vendorOrganizationFactors']['annualRevenue']
    except:
        return None
    
@catch_key_error
def get_number_of_employees(award):
    print("got to get_number_of_employees")
    try:
        return award['vendor']['vendorSiteDetails']['vendorOrganizationFactors']['numberOfEmployees']
    except:
        return None
    
@catch_key_error
def get_last_modified_by(award):
    print("got to get_last_modified_by")
    try:
        return award['transactionInformation']['lastModifiedBy']
    except:
        return None
    
def get_contract_pricing_name(award):
    print("got to get_contract_pricing_name")
    @catch_key_error
    def get_name(award):
        return award['contractData']['typeOfContractPricing']

    name = get_name(award) 
    if name and type(name) == str:
        return name

    elif name:
        try:
            return award['contractData']['typeOfContractPricing']['@description']
        except:
            return award['contractData']['typeOfContractPricing']
        
@catch_key_error
def get_contract_pricing_id(award):
    print("got to get_contract_princing_id")
    try:
        return award['contractData']['typeOfContractPricing']['#text']
    except:
        return None
    
@catch_key_error
def get_reason_for_modification(award):
    print("got to get_reason_for_modification")
    try:
        return award['contractData']['reasonForModification']['#text']
    except:
        return None
    
def get_naics(award):
    print("got to get_naics")
    #this is failing for some reason
    @catch_key_error
    def get_name(award):
        return award['productOrServiceInformation']['principalNAICSCode']

    name = get_name(award) 
    if name and type(name) == str:
        return name

    elif name:
        try:
            return award['productOrServiceInformation']['principalNAICSCode']['#text']
        except:
            return award['productOrServiceInformation']['principalNAICSCode']
    
@catch_key_error
def get_psc(award):
    print("got to get_psc")
    try:
        return award['productOrServiceInformation']['productOrServiceCode']['#text']
    except:
        return None

def last_load(load_all=False):
    print("got to last_load")
    load = FPDSLoad.objects.all().order_by('-load_date')
    if len(load) > 0 and not load_all:
        return load[0].load_date    
    else: 
        today = datetime.now()
        return  today - timedelta(weeks=(52*10))


def create_load(load_date):
    print("got to create_load")
    #overwrite the most recent load object to keep the table from growing 
    load = FPDSLoad.objects.all().order_by('-load_date')
    if len(load) > 0:
        load_obj = load[0]
    else:
        load_obj = FPDSLoad()

    load_obj.load_date = load_date
    load_obj.save()

class Command(BaseCommand):
    
    logger = logging.getLogger('fpds')
    contracts = Contracts()

    option_list = BaseCommand.option_list \
                  + (make_option('--load_all', action='store_true', dest='load_all', default=False, help="Force load of all contracts"), ) \
                  + (make_option('--id', action='store', type=int,  dest='id', default=1, help="load contracts for vendors greater or equal to this id"), )

    def date_format(self, date1, date2):
        return "[{0},{1}]".format(date1.strftime("%Y/%m/%d"), date2.strftime("%Y/%m/%d"))

    def handle(self, *args, **options):
  
        print("-------BEGIN LOAD_FPDS PROCESS-------")
        try:

            if 'load_all' in options:
                load_from = last_load(options['load_all'])
            else:
                load_from = last_load()
            
            load_to = datetime.now()
           
            #allow to start from a certain vendor
            if 'id' in options:
                print("inside if-statement: filter by vendor_id and order_by id")
                #vendor_id = int(options['id'])
                vendors = Vendors.objects.all()#filter(id__gte=vendors_id)#.order_by('id')
                print("Size of vendors object:",len(vendors))
            else:
                print("order_by id")
                vendors = Vendors.objects.all()#.order_by('id')
                print("Size of vendors object:",len(vendors))

            for outter_ind,v in enumerate(vendors):
                print("inside outter for loop:",outter_ind)
                by_piid = {}
                try:
                    v_con = self.contracts.get(vendors_duns=v.duns, last_modified_date=self.date_format(load_from, load_to), num_records='all')
                except:
                    pass
                    
                for first_inner_ind,vc in enumerate(v_con):
                    print("inside inner for loop:",first_inner_ind)
                    con_type = ''
                    if 'IDV' in vc['content']:
                        continue # don't get IDV records

                    try:
                        award = vc['content']['award']
                    
                    except KeyError:
                        try:
                            award = vc['content']['OtherTransactionAward']
                        except KeyError:
                            print(vc)
                            continue 
                        
                    
                    award_id = get_award_id_obj(award)
                    piid = get_piid(award_id)

                    if 'contractDetail' in award:
                        award = award['contractDetail'] # for OtherTransactionAward, details are nested one more level

                    record = {
                        'mod_number': get_mod(award_id), 
                        'transaction_number': get_transaction_number(award_id),
                        'ultimate_completion_date': get_ultimate_completion_date(award), 
                        'current_completion_date': get_current_completion_date(award), 
                        'signed_date': award['relevantContractDates']['signedDate'],
                        'agency_id': get_agency_id(award_id), #award_id['awardContractID']['agencyID']['#text'],
                        'agency_name': get_agency_name(award_id), #award_id['awardContractID']['agencyID']['@name'],
                        'obligated_amount': award['dollarValues']['obligatedAmount'],
                        'annual_revenue': get_annual_revenue(award),
                        'number_of_employees': get_number_of_employees(award),
                        'last_modified_by': get_last_modified_by(award),
                        'reason_for_modification': get_reason_for_modification(award),
                        'type_of_contract_pricing_name': get_contract_pricing_name(award),
                        'type_of_contract_pricing_id': get_contract_pricing_id(award),
                        'naics' : get_naics(award),
                        'psc': get_psc(award),
                    }
                    
                    if piid in by_piid:
                        by_piid[piid].append(record)
                    else:
                        by_piid[piid] = [record, ]
                counter = 0
                for piid, records in by_piid.items():
                    counter += 1
                    print("inside second inner for-loop:",counter)
                    by_piid[piid] = sorted(records, key=lambda x: (x['mod_number'], x['transaction_number']))
                    total = 0 # amount obligated
                    
                    self.logger.debug("================{0}===Vendor {1}=================\n".format(piid, v.duns))

                    self.logger.debug(self.contracts.pretty_print(by_piid[piid]))
                    print("got to contract get or create")
                    con, created = Contract.objects.get_or_create(piid=piid, vendors=v)
                    print("completed contract get or create")
                    for mod in by_piid[piid]:
                        total += float(mod.get('obligated_amount'))
                        con.date_signed = mod.get('signed_date') 
                        con.completion_date = mod.get('current_completion_date') or mod.get('ultimate_completion_date')
                        con.agency_id = mod.get('agency_id')
                        con.agency_name = mod.get('agency_name')
                        con.pricing_type = mod.get('type_of_contract_pricing_id')
                        con.pricing_type_name = mod.get('type_of_contract_pricing_name')

                        if mod.get('reason_for_modification') in ['X', 'E', 'F']:
                            con.reason_for_modification = mod.get('reason_for_modification')
                        else:
                            if con.completion_date:
                                date_obj = datetime.strptime(con.completion_date, '%Y-%m-%d %H:%M:%S')
                                today = datetime.utcnow()
                                if date_obj:
                                    if date_obj > today:
                                        con.reason_for_modification = 'C2'
                                    else:
                                        con.reason_for_modification = 'C1'

                        if mod.get('last_modified_by') and '@' in mod['last_modified_by'].lower():
                            #only add if it's an actual email, make this a better regex
                            con.last_modified_by = mod['last_modified_by']
                        
                        #ADD NAICS -- need to add other naics as objects to use foreignkey
                        con.PSC = mod.get('psc')
                        con.NAICS = mod.get('naics')

                        ar = mod.get('annual_revenue') or None
                        ne = mod.get('number_of_employees') or None
                        if ar:
                            v.annual_revenue = int(ar)

                        if ne:
                            v.number_of_employees = int(ne)

                    con.obligated_amount = total
                    con.save()

                #save updates to annual revenue, number of employees
                v.save()
            create_load(load_to)

        except Exception as e:
            print("MAJOR ERROR -- PROCESS ENDING EXCEPTION --  {0}".format(e))
            import sys
            traceback.print_tb(sys.exc_info()[2])
            self.logger.debug("MAJOR ERROR -- PROCESS ENDING EXCEPTION -- {0}".format(e))
            print("got to end of process, with exception")
        print("-------END LOAD_FPDS PROCESS-------")

