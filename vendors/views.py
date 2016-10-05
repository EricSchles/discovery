from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from Vendors.models import Vendors, Pool, Naics, SetAside
from contract.models import Contract
import csv
from titlecase import titlecase

def pool_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search_results.csv"'
    writer = csv.writer(response)
    #write results
    Vendors = Vendors.objects.all()
    setasides_all = SetAside.objects.all().order_by('far_order')
    filter_text = []
    #naics
    naics = Naics.objects.get(short_code=request.GET['naics-code'])
    vehicle = request.GET['vehicle'].upper()
    pool = Pool.objects.get(naics=naics, vehicle=vehicle) 
    Vendors = Vendors.filter(pools=pool)
    filter_text.append("NAICS code {0}".format(naics))
    
    #setasides
    if 'setasides' in request.GET:
        setasides = request.GET.getlist('setasides')[0].split(',')
        setaside_objs = SetAside.objects.filter(code__in=setasides)
        for sobj in setaside_objs:
            Vendors = Vendors.filter(setasides=sobj)

        filter_text.append("Set Aside filters: {0}".format(", ".join(setasides)))

    writer.writerow(("Vehicle: " + vehicle,))
    writer.writerow(("Search Results: {0} Vendors".format(len(Vendors)),))
    writer.writerow(filter_text)

    writer.writerow(('',))
    header_row = ['Vendors', 'Location', 'No. of Contracts',]
    header_row.extend([sa_obj.abbreviation for sa_obj in setasides_all])
    writer.writerow(header_row)

    lines = []

    for v in Vendors: 
        setaside_list = []
        for sa in setasides_all:
            if sa in v.setasides.all():
                setaside_list.append('X')
            else:
                setaside_list.append('')

        v_row = [v.name, v.sam_citystate, Contract.objects.filter(NAICS=naics.code, Vendors=v).count()]
        v_row.extend(setaside_list)
        lines.append(v_row)

    lines.sort(key=lambda x: x[2], reverse=True)
    for line in lines:
        writer.writerow(line)

    return response


def Vendors_csv(request, Vendors_duns):
    Vendors = Vendors.objects.get(duns=Vendors_duns)
    setasides = SetAside.objects.all().order_by('far_order')

    naics = request.GET.get('naics-code', None)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search_results.csv"'
    writer = csv.writer(response)

    writer.writerow((Vendors.name,))
    writer.writerow(('SAM registration expires: ', Vendors.sam_expiration_date.strftime("%m/%d/%Y")))
    writer.writerow(('', ))
    writer.writerow([sa_obj.abbreviation for sa_obj in setasides])

    Vendors_sa = []
    for sa in  setasides:
        if sa in Vendors.setasides.all():
            Vendors_sa.append('X')
        else:
            Vendors_sa.append('')

    writer.writerow(Vendors_sa)
    writer.writerow(('', ))
    writer.writerow(('DUNS', Vendors.duns, '', 'Address:', titlecase(Vendors.sam_address)))
    writer.writerow(('CAGE Code', Vendors.cage, '', '',  titlecase(Vendors.sam_citystate[0:Vendors.sam_citystate.index(',') + 1]) + Vendors.sam_citystate[Vendors.sam_citystate.index(',') + 1:]))
    writer.writerow(('Employees', Vendors.number_of_employees, '', 'OASIS POC:', Vendors.pm_name))
    writer.writerow(('Annual Revenue', Vendors.annual_revenue, '', '', Vendors.pm_phone))
    writer.writerow(('', '', '', '', Vendors.pm_email.lower()))
    writer.writerow(('', ))
    if naics:
        writer.writerow(('This Vendors\'s contract history for NAICS {0}'.format(naics), ))
    else:
        writer.writerow(('This Vendors\'s contract history for all contracts', ))
        
    writer.writerow(('Date Signed', 'PIID', 'Agency', 'Type', 'Value ($)', 'Email POC', 'Status'))

    if naics:
        contracts = Contract.objects.filter(Vendors=Vendors, NAICS=naics).order_by('-date_signed')
    else:
        contracts = Contract.objects.filter(Vendors=Vendors).order_by('-date_signed')
    for c in contracts:
        if '_' in c.piid:
            piid = c.piid.split('_')[1]
        else:
            piid = c.piid
        writer.writerow((c.date_signed.strftime("%m/%d/%Y"), piid, titlecase(c.agency_name), c.get_pricing_type_display(), c.obligated_amount, (c.point_of_contact or "").lower(), c.get_reason_for_modification_display()))

    return response


