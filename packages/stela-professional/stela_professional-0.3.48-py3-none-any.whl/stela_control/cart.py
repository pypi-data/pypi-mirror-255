from datetime import datetime
from decimal import Decimal
from xml import dom
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from requests import request
from stela_control.models import StelaSelection, ProStelaData, Notifications
from django.conf import settings
from stela_control.models import Company
from stela_control.forms import NewsletterForm
from accounts.models import UserBase
import requests


class Cart():
    
    def __init__(self, request):
        self.session = request.session

        stela = self.session.get(settings.CART_SESSION)
        if settings.CART_SESSION not in request.session:
            stela = self.session[settings.CART_SESSION] = {}
        self.stela = stela

        # store = self.session.get(settings.STELA_SESSION)
        # if settings.STELA_SESSION not in request.session:
        #     store = self.session[settings.STELA_SESSION] = {}
        # self.store = store

        alert = self.session.get(settings.ALERT_SESSION)
        if settings.ALERT_SESSION not in request.session:
            alert = self.session[settings.ALERT_SESSION] = {}
        self.alert = alert


    def service_add (self, selectid):
       
        select_id = str(selectid)
        if select_id is not self.stela:
            self.stela[select_id] = {}
       
        self.save()
    
    def alert_add (self, alertid):
       
        alert_id = str(alertid)
        if alert_id is not self.alert:
            self.alert[alert_id] = {}
       
        self.save()
    
    def product_add (self, productid):
       
        select_id = str(productid)
        if select_id is not self.store:
            self.store[select_id] = {}
       
        self.save()

    def get_service(self):
        select_ids = self.stela.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        return selections

    def get_alerts(self):
        alert_ids = self.alert.keys()
        alerts = Notifications.objects.filter(id__in=alert_ids)
        get_alerts = self.stela.copy()
        
        
        for alert in alerts:
            get_alerts[str(alert.id)]['alert'] = alert
        
        
        for item in get_alerts.values():
            
            yield item    
    
    def __len__(self):
        select_ids = self.stela.keys()
        # products = StoreSelection.objects.filter(id__in=select_ids)
        selections = StelaSelection.objects.filter(id__in=select_ids)
        return selections.count()
    
    def alert_count(self):
        alert_ids = self.alert.keys()
        alerts = Notifications.objects.filter(id__in=alert_ids)
        return alerts.count()

    def serviceData(self):
        select_ids = self.stela.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        return selections

    def service_sub(self):
        select_ids = self.stela.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        service_cost = sum([item.amount for item in selections])
        subtotal = service_cost
        return round(subtotal, 2)
    
    def service_tax(self):
        subtotal = self.service_sub()
        taxes = subtotal * Decimal(0.10)
        return round(taxes, 2)
    
    def service_fee(self):
        subtotal = self.service_sub()
        taxes = self.service_tax()
        base = subtotal + taxes
        fee = base * Decimal(0.02)
        return round(fee, 2)
    
    def service_total(self):
        subtotal = self.service_sub()
        taxes = self.service_tax()
        fee = self.service_fee()
        total = subtotal + taxes + fee
        return round(total, 2)
    
    def import_sub(self):
        select_ids = self.stela.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        service_cost = sum([item.amount for item in selections])
        subtotal = service_cost / 2
        return round(subtotal, 2)
    
    def import_tax(self):
        subtotal = self.import_sub()
        taxes = subtotal * Decimal(0.10)
        return round(taxes, 2)
    
    def import_fee(self):
        subtotal = self.import_sub()
        taxes = self.import_tax()
        base = subtotal + taxes
        fee = base * Decimal(0.02)
        return round(fee, 2)
    
    def import_total(self):
        subtotal = self.import_sub()
        taxes = self.import_tax()
        fee = self.import_fee()
        total = subtotal + taxes + fee
        return round(total, 2)

    def servicio_base(self):
        url = settings.VES_MONITOR
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            currency=Decimal(data['USD']['promedio_real'])
        else:
            currency=Decimal(24.48)
            
        select_ids = self.stela.keys()
        selections = StelaSelection.objects.filter(id__in=select_ids)
        service_cost = sum([item.amount for item in selections])
        subtotal = service_cost / 2
        calc=subtotal * currency
        return round(calc, 2)

    def servicio_iva(self):
        subtotal = self.servicio_base()
        taxes = subtotal * Decimal(0.16)
        return round(taxes, 2)
    
    def servicio_fee(self):
        subtotal = self.servicio_base()
        fee = subtotal * Decimal(0.02)
        return round(fee, 2)
        
    def total_ves(self):
        subtotal = self.servicio_base()
        taxes = self.servicio_iva()
        fee = self.servicio_fee()
        total = subtotal + taxes + fee
        return round(total, 2)
    
    def stela_del(self, obj):

        select_id = str(obj)
        
        if select_id in self.stela:
           del self.stela[select_id]
        self.save()  

    def save(self):
        self.session.modified = True 
    
    def stela_clear(self):
        del self.session[settings.CART_SESSION]
        self.save()
   
class SiteData():

    def __init__(self, request):
        user = request.user
        self.user_id = request.session['user_id'] = user.id

        self.session = request.session
        self.lang = request.LANGUAGE_CODE
        data = self.session.get(settings.DATA_ID)
        
        if settings.DATA_ID not in request.session:
            data = self.session[settings.DATA_ID] = {}
        self.data = data
    
    def admin(self):
        owner = UserBase.objects.get(id=self.user_id)
        return owner
    
    def company_public(self):
        owner=UserBase.objects.get(is_superuser=True)
        company = Company.objects.filter(owner=owner, lang=self.lang).last()
        return company
    
    # def company_billing(self):
    #     owner = UserBase.objects.get(id=self.user_id)
    #     company = Company.objects.filter(owner=owner).last()
    #     return company
    

    # def blogs(self):
    #     get_blogs = News.objects.filter(status="Publish").order_by('-created')[:10]
    #     return get_blogs
    
    # def form(self):
    #     form = DataEmailForm()
    #     return form
    def lang(self):    
        lang = self.lang
        return lang 

    def chat(request):
        user_id = request.session.get('user_id')
        queries=ProStelaData.objects.filter(user=user_id)
        return queries
    
    def form(self):
        form = NewsletterForm()
        return form