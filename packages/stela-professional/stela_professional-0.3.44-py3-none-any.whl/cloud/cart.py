from decimal import Decimal
from stela_control.models import StelaSelection
from django.conf import settings

class CartCloud():

    def __init__(self, request):
        self.session = request.session

        select = self.session.get(settings.CLOUD_SESSION)
        if settings.CLOUD_SESSION not in request.session:
            select = self.session[settings.CLOUD_SESSION] = {}
        self.select = select

    def selection_add(self, integration):
        
        integration_id = str(integration)
        if integration_id is not self.select:
            self.select[integration_id] = {}


    def service_add (self, count, selectid):
       
        select_id = str(selectid)
        if select_id is not self.select:
            self.select[select_id] = {'count':int(count)}
       
        self.save()

    def get_select(self):
        select_ids = self.select.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        get_select = self.select.copy()
        
        
        for select in selections:
            get_select[str(select.id)]['select'] = select
        
        
        for item in get_select.values():
            
            yield item
    
    def __len__(self):
        
        return sum(item['count'] for item in self.select.values())
    
    def data(self):
        select_ids = self.select.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        return selections

    def get_subtotal(self):
        select_ids = self.select.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        service_cost = sum([item.amount for item in selections])
        subtotal = service_cost
        return round(subtotal, 2)
    
    def get_taxes(self):
        subtotal = self.get_subtotal()
        taxes = subtotal * Decimal(0.10)
        return round(taxes, 2)
    
    def get_payment_fee(self):
        subtotal = self.get_subtotal()
        taxes = self.get_taxes()
        base = subtotal + taxes
        fee = base * Decimal(0.02)
        return round(fee, 2)
    
    def get_total_price(self):
        subtotal = self.get_subtotal()
        taxes = self.get_taxes()
        fee = self.get_payment_fee()
        total = subtotal + taxes + fee
        return round(total, 2)

    def get_base(self):
        select_ids = self.select.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        service_cost = sum([item.amount for item in selections])
        subtotal = service_cost * Decimal(18.56)
        return round(subtotal, 2)

    def iva(self):
        subtotal = self.get_base()
        taxes = subtotal * Decimal(0.16)
        return round(taxes, 2)
    
    def fee(self):
        subtotal = self.get_base()
        fee = subtotal * Decimal(0.02)
        return round(fee, 2)
        
    def total_ves(self):
        subtotal = self.get_base()
        taxes = self.iva()
        fee = self.fee()
        total = subtotal + taxes + fee
        return round(total, 2)
    
    def delete(self, select):

        select_id = str(select)
        
        if select_id in self.select:
           del self.select[select_id]
        self.save()  

    def save(self):
        self.session.modified = True 
    
    def clear(self):
        del self.session[settings.SESSION_ID]
        self.save()