from django.db import models
from django.db.models import Avg, Count
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.conf import settings
from .functions import caption_optimizer
from django.urls import reverse
from django.db.models import Sum
from cloud.models import Domains, UsageCloud
from geolocation.models import Country, City
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from django.template.defaultfilters import slugify
from datetime import datetime, timedelta
from django.utils import timezone
import os
from django.utils.crypto import get_random_string

# from siteapp.models import Order

#Inventory
class Category(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    TYPE = (
        ('woman', _('woman')),
        ('male', _('male')),
        ('curvy', _('curvy')),
        ('kids', _('kids')),
        ('furniture', _('furniture')),
        ('Select Type', _('Select Type')),
        ('Consulting', _('Consulting')),
    )
    type = models.CharField(max_length=30, choices=TYPE, default=_("Select Type"), verbose_name=_("Type"))
    title = models.CharField(max_length=50, verbose_name=_("Title"))
    slug = models.SlugField(max_length=255, help_text=_("Required"))
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)
    lang = models.CharField(max_length=80, default="en")


    def __str__(self):
        return self.type + ' ' + self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

class Inventory(models.Model):
    STATUS = (
        ('Active', _('Active')),
        ('Pending', _('Pending')),
        ('Inactive', _('Inactive')),
    )
    TYPE = (
        ('Service', _('Service')),
        ('Product', _('Product')),
        ('Publishing', _('Publishing')),
        ('Reviews Works', _('Reviews Works')),
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True)
    status = models.CharField(max_length=10, choices=STATUS, verbose_name=_("Status"), default=_("Inactive")) 
    sku = models.CharField(verbose_name=_("SKU"), help_text=_("Required"), max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_("Title"), help_text=_("Required"), max_length=255)
    yearly = models.BooleanField(default=False,)
    type = models.CharField(max_length=30, choices=TYPE, default=_("Select Type"), verbose_name=_("Type"))
    description = models.TextField(verbose_name=_("Description"), help_text=_("No Required"), blank=True)
    image = models.ImageField(verbose_name=_("Image"), upload_to='inventory/')
    qty = models.IntegerField(verbose_name=_('Quantity'), blank=True, null=True)
    slug = models.SlugField(max_length=255, help_text=_("Required"))
    price = models.DecimalField(blank=True, null=True, verbose_name=_("Price USD"), help_text=_("Maximun 9999.99"), error_messages={
        "name": {
            "max_lenght": _("The price must be between 0 and 9999.99"),
        },
    },
    max_digits=6,
    decimal_places=2,
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False) 
    url = models.URLField()
    published_date=models.DateTimeField(_("Published Date"), blank=True, null=True)
    updated_at = models.DateTimeField(_("Updated"), auto_now=True)
    lang = models.CharField(max_length=80, default="en")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Inventory, self).save(*args, **kwargs)

    class Meta:
        ordering = ("-created",)
    
    def __str__(self):
        return self.sku+' - '+self.title

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""
    
    def qty(self):
        total_qty=Variant.objects.filter(product_id=self.pk).aggregate(total=(Sum('quantity')))
        qty = total_qty['total']
        return qty

    def avaregereview(self):
        reviews = Reviews.objects.filter(catalog=self, status='Publish').aggregate(avarage=Avg('rate'))
        avg=0
        if reviews["avarage"] is not None:
            avg=float(reviews["avarage"])
        return avg

    def countreview(self):
        reviews = Reviews.objects.filter(catalog=self, status='Publish').aggregate(count=Count('id'))
        cnt=0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt
    
    def get_absolute_url(self):
        return reverse('home:work-detail', kwargs={'pk': self.pk, 'slug': self.slug})
    
class StelaColors(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=20)
    code1 = models.CharField(max_length=10, blank=True,null=True)
    code2 = models.CharField(max_length=10, blank=True,null=True)
    code3 = models.CharField(max_length=10, blank=True,null=True)

    
    def __str__(self):
        return self.name

    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""

class Bulletpoints(models.Model):
    product=models.ForeignKey(Inventory, on_delete=models.CASCADE)
    text = models.CharField(max_length=250, blank=True, verbose_name=_('Bulletpoint'))
   
class Sizes(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    size = models.CharField(max_length=20, verbose_name=_('size'))

    def __str__(self):
        return self.size

class Variant(models.Model):
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='variant')
    color = models.CharField(max_length=50, verbose_name=_("Color"), blank=True, null=True)
    size = models.CharField(max_length=50, verbose_name=_("Size"), blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Variant Price USD"))
    image = models.ImageField(verbose_name=_("Variant Image"), upload_to='inventory/variants/', null=True, blank=True)
    sku = models.CharField(max_length=255, verbose_name=_("SKU"), blank=True, null=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_("Weight (kg)"))
    material = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Material"))
    warranty = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Warranty Information"))    
    technical_specs = models.TextField(verbose_name=_("Technical Specifications"), blank=True)  
    safety_information = models.TextField(verbose_name=_("Safety Information"), blank=True)
    compliance_certificates = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Compliance Certificates"))

    def __str__(self):
        return "{} - {} - {}".format(self.product.title, self.color, self.size)

    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""
        
class Elements(models.Model):
    STATUS = (
        ('Active', _('Active')),
        ('Inactive', _('Inactive')),
    )

    parent = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='elements')
    title = models.CharField(verbose_name=_("Service"), help_text=_("Required"), max_length=255)
    subtitle = models.CharField(verbose_name=_("Subtitle"), help_text=_("Required"), max_length=255)
    content = models.TextField(verbose_name=_("Description"), help_text=_("No Required"), blank=True)
    image = models.ImageField(verbose_name=_("Image"), upload_to='services/')
    price = models.DecimalField(blank=True, null=True, verbose_name=_("Price USD"), help_text=_("Maximun 9999.99"), error_messages={
        "name": {
            "max_lenght": _("The price must be between 0 and 9999.99"),
        },
    },
    max_digits=6,
    decimal_places=2,
    )
    status = models.CharField(max_length=10, choices=STATUS)
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False) 
    slug = models.SlugField(max_length=255, blank=True)

    def __str__(self):
        return self.title + ' - '+ '$' + str(self.price)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Elements, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('home:service-detail', kwargs={'pk': self.pk, 'slug': self.slug})
    
class VariantsImage(models.Model):
    product=models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='catalog')
    title = models.CharField(max_length=255, verbose_name=_('Catalogue Title'))
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Gallery(models.Model):
    TYPE = (
        ('Product Detail', _('Product Detail')),
        ('Product Description', _('Product Description')),
    )
    type = models.CharField(max_length=30, choices=TYPE, default=_("Select Type"), verbose_name=_("Type"))
    catalogue=models.ForeignKey(VariantsImage, on_delete=models.CASCADE, blank=True, null=True, related_name='img')
    title = models.CharField(max_length=255, default='No selected')
    image = models.ImageField(blank=True, upload_to='product/')

    def __str__(self):
        return self.title + ' ' + self.catalogue.title

class CommentsWorks(models.Model):
    parent = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="comments", null=True)
    full_name = models.CharField(max_length=250)
    cover = models.ImageField(verbose_name=_("Profile"), upload_to='comment_profile/')
    content = models.TextField(verbose_name=_('Message'))

class Reviews(models.Model):
    POST_STATUS_CHOICES=(
        ('Draft', _('Draft')),
        ('Publish', _('Publish'))
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    catalog = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="reviews", null=True)
    rate = models.IntegerField(default=1)
    status = models.CharField(max_length=10, choices=POST_STATUS_CHOICES, default="Draft") 
    lang = models.CharField(max_length=80)
    content = models.TextField(verbose_name=_('Message'))
    create=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user + self.rate
  
class Templates(models.Model):
    STATUS = (
        ('Inactive', 'Inactive'),
        ('Active', 'Active'),
    )
    status = models.CharField(max_length=10, choices=STATUS, default="Inactive", verbose_name=_('Status'))
    title = models.CharField(max_length=150, blank=False, verbose_name=_("Title"))
    image = models.ImageField(verbose_name=_("Image"), upload_to='templates/')
    slug = models.SlugField(max_length=255, help_text=_("Required"))
    url = models.CharField(max_length=50, blank=False, verbose_name="Url")
    integration = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='items', null=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Templates, self).save(*args, **kwargs)

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""
        
class StelaSelection(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Checked', 'Checked'),
        ('Payeed', 'Payeed'),
    )
    validator = models.CharField(max_length=50, default="No user")
    status = models.CharField(max_length=10, choices=STATUS, default="Pending")
    integration = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True)
    domain = models.ForeignKey(Domains, on_delete=models.CASCADE, null=True)
    template = models.ForeignKey(Templates, on_delete=models.CASCADE, related_name='templates', null=True)
    amount = models.DecimalField(blank=True, null=True, error_messages={
        "name": {
            "max_lenght": _("The price must be between 0 and 9999.99"),
        },
    },
    max_digits=6,
    decimal_places=2,
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.integration.title)

class StelaItems(models.Model):
    parent = models.ForeignKey(StelaSelection, on_delete=models.CASCADE, related_name='parent')
    module = models.CharField(max_length=150, blank=False, verbose_name="Title")
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)

class Customer(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=250, verbose_name=_('Full Name'))
    userid = models.CharField(max_length=20, verbose_name=_('Costumer ID'))
    email = models.EmailField(_('email'))
    country_profile = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=150, verbose_name=_('Address'))
    phone = models.CharField(max_length=50, verbose_name=_('phone_number'))

    def __str__(self):
        return self.full_name + ' - ' + self.userid

#Billing
class BillingRecipt(models.Model):
    OPTION ={
        ('budget_design',_('Budget Design')),
        ('budget_marketing',_('Budget Marketing')),
        ('budget_development',_('Budget Development')),
        ('Billing receipt',_('Billing receipt')),
        ('Monthly charge',_('Monthly charge')),
        ('Others',_('Others')),
    }
    is_generated=models.BooleanField(default=False)
    is_budget=models.BooleanField(default=False)
    status = models.CharField(max_length=60, default="Pending")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer")
    payment_option = models.CharField(max_length=200, blank=True, null=True)
    option = models.CharField(max_length=60, choices=OPTION, verbose_name=_('Case'), null=True)
    report = models.TextField(verbose_name=_('Report'), null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.created)

class ItemServices(models.Model):
    recipt = models.ForeignKey(BillingRecipt, related_name='service_recipt', on_delete=models.CASCADE)
    field = models.ForeignKey(Elements, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    qty = models.IntegerField(default=1, verbose_name=_("Qty"))

class ItemProducts(models.Model):
    recipt = models.ForeignKey(BillingRecipt, related_name='product_recipt', on_delete=models.CASCADE)
    field = models.ForeignKey(Variant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    qty = models.IntegerField(default=1, verbose_name=_("Qty"))

class ItemCloud(models.Model):
    recipt = models.ForeignKey(BillingRecipt, related_name='cloud_recipt', on_delete=models.CASCADE)
    field = models.ForeignKey(UsageCloud, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    qty = models.IntegerField(default=1, verbose_name=_("Qty"))

class TemplateSections(models.Model):
    section = models.CharField(max_length=80, verbose_name=_('Section'))
    lang = models.CharField(max_length=80, default="en")
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.section

class BudgetControl(models.Model):
    recipt = models.ForeignKey(BillingRecipt, related_name="budget_control", on_delete=models.CASCADE)
    control_id = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.control_id + str('') + self.recipt.customer.userid)
    
class ModuleItems(models.Model):
    recipt = models.ForeignKey(BillingRecipt, related_name='modules', on_delete=models.CASCADE)
    field = models.ForeignKey(Elements, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    qty = models.IntegerField(default=1, verbose_name=_("Qty"))

class ItemDiscount(models.Model):
    OPTION ={
        ('Initial Payment','Initial Payment'),
        ('Promotional Discount','Promotional Discount'),
        ('Stela Payment Free Suscription','Stela Payment Free Suscription'),
        ('No Selected','No Selected'),
        
    }
    recipt = models.ForeignKey(BillingRecipt, related_name='discounts', on_delete=models.CASCADE)
    field = models.CharField(max_length=60, choices=OPTION)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

class Order(models.Model):
    STATUS = {
        ('Completed','Completed'),
        ('Pending','Pending'),
    }
    CHOICES = {
        ('Stela Websites','Stela Websites'),
        ('Stela Marketing','Stela Marketing'),
        ('Stela Design','Stela Design'),
        ('Cloud Elastic Instance','Cloud Elastic Instance'),
        ('Cloud Domains','Cloud Domains'),
        ('Store','Store'),
        ('No Selected','No Selected'),
    }
    section = models.CharField(max_length=50, default="No Selected", choices=CHOICES)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    email = models.EmailField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    key_validator = models.CharField(max_length=200)
    transaction_id = models.CharField(max_length=200, null=True)
    payment_option = models.CharField(max_length=200, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    taxes = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    profit = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    payment_fee = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    total_paid = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    status = models.CharField(max_length=100, default="Pending", choices=STATUS)
    billing=models.IntegerField(null=True)
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.created)
    
class OrderItems(models.Model):
    nameitem=models.CharField(max_length=200)
    order = models.ForeignKey(Order, related_name='purchases', on_delete=models.CASCADE)
    product = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    elements = models.ForeignKey(Elements, on_delete=models.CASCADE, null=True)
    stela_selection = models.ForeignKey(StelaSelection, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)

class StelaPayments(models.Model):
    order=models.IntegerField(null=True)
    billing=models.IntegerField(null=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    key_validator = models.CharField(max_length=200)
    transaction_id = models.CharField(max_length=200, null=True)
    payment_option = models.CharField(max_length=200, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    taxes = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    profit = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    payment_fee = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    total_paid = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    host = models.CharField(max_length=200)
     
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.created)

class InvoiceControl(models.Model):
    recipt = models.ForeignKey(BillingRecipt, related_name="billing_control", on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    control_id = models.CharField(max_length=20, default="Not ID")
    section = models.CharField(max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.control_id + str('') + self.recipt.customer.userid)

class ControlFacturacion(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    customer=models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    origin = models.ForeignKey(BillingRecipt, on_delete=models.CASCADE, null=True, related_name='control')
    control_id=models.CharField(max_length=15)
    base=models.DecimalField(max_digits=8, decimal_places=2, null=True)
    iva=models.DecimalField(max_digits=8, decimal_places=2, null=True)
    total=models.DecimalField(max_digits=15, decimal_places=2, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.created)

class FacturaItems(models.Model):
    order = models.ForeignKey(ControlFacturacion, related_name='compra', on_delete=models.CASCADE)
    recipt = models.ForeignKey(InvoiceControl, on_delete=models.CASCADE, null=True)
    origin = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.created)

class PathControl(models.Model):
    STEPS = {
        ('Step 2','Step 2'),
        ('Step 3','Step 3'),
        ('Step 4','Step 4'),
    }
    order = models.ForeignKey(Order, related_name='path', on_delete=models.CASCADE)
    step = models.CharField(max_length=50, default="No Selected", choices=STEPS)
    superuser = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=200, null=True)
    url = models.CharField(max_length=200, null=True)
    
class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    withdraw = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.date

#userData
class Contact(models.Model):
    POST_STATUS_CHOICES=(
        ('Answered',_('Answered')),
        ('No Answered',_('No Answered'))
    )

    status = models.CharField(max_length=20, choices=POST_STATUS_CHOICES, verbose_name=_('Status'), default="No Answered")
    name = models.CharField(max_length=150, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(verbose_name='Email')
    subject = models.CharField(max_length=150, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message'))

    def __str__(self):
        return self.subject
    
class ContactResponse(models.Model):
    parent = models.ForeignKey(Contact, related_name="contact_response", on_delete=models.CASCADE)
    message = models.TextField(verbose_name=_('Response'))

class WishList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="whishlist")
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False) 

    class Meta:
        ordering = ("-created",)
    
    def __str__(self):
        return self.product

class Company(models.Model):
    CHOICES = {
        (_('E-commerce'),_('E-commerce')),
        (_('Restaurants and Food Services'),_('Restaurants and Food Services')),
        (_('Consulting'),_('Consulting')),
        (_('Health and Wellness'),_('Health and Wellness')),
        (_('IT Development Services'),_('IT Development Services')),
        (_('Education and Training'),_('Education and Training')),
        (_('Marketing and Advertising Services'),_('Marketing and Advertising Services')),
        (_('Beauty and Personal Care Services'),_('Beauty and Personal Care Services')),
        (_('Repair and Maintenance Services'),_('Repair and Maintenance Services')),
        (_('Logistics and Transportation Services'),_('Logistics and Transportation Services')),
        (_('Media Creators'),_('Media Creators')),
    }
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company")
    name = models.CharField(max_length=200, verbose_name=_('Startup Name'))
    business = models.CharField(max_length=100, choices=CHOICES, verbose_name=_('Business Type'), blank=True, null=True)
    main_logo = models.ImageField(upload_to='brands/', verbose_name=_('Brand Logo'))
    alter_logo = models.ImageField(upload_to='brands/', verbose_name=_('Brand Logo'))
    content = models.TextField()
    web = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, verbose_name=_('Contact email'))
    phone = models.CharField(max_length=20)
    country_legal = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.CASCADE, blank=True, null=True)
    city_legal = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=500)
    lang = models.CharField(max_length=80, default="en")
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name 

class Team(models.Model):
    STATUS = (
        ('Publish', _('Publish')),
        ('Draft', _('Draft')),
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="owner_team")
    status = models.CharField(max_length=10, choices=STATUS, default="Draft", verbose_name=_('Status'))
    full_name = models.CharField(max_length=150, blank=False, verbose_name=_('Staff Full Name'))
    content = models.TextField()
    image = models.ImageField(verbose_name=_("Image"), upload_to='profile/')
    lang = models.CharField(max_length=80, default="es")
    staff = models.CharField(max_length=150, blank=False, verbose_name=_('Staff'))
    
    def __str__(self):
        return self.full_name
    
    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
    
class ProfileGallery(models.Model):
    profile=models.ForeignKey(Team, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(verbose_name=_("Image"), upload_to='profile_gallery/', null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    
class SocialLinks(models.Model):
    OPTION ={
        ('X','X'),
        ('Facebook','Facebook'),
        ('Instagram','Instagram'),
        ('Wikipedia','Wikipedia'),
        ('Tiktok','Tiktok'),
        ('Youtube','Youtube'),
        ('Linkedin','Linkedin'),
        ('Github','Github'),
    }
    parent_staff = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="staff_social")
    parent_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="owner_social")
    parent_company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, related_name="company_social")
    social=models.CharField(max_length=50, default="No Selected", choices=OPTION)
    url=models.CharField(max_length=80)

    def __str__(self):
        return self.parent.name + ' ' + self.social

class ClubPoints(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    points = models.IntegerField()
        
class Addresses(models.Model):
    status =  models.CharField(max_length=50, default="Not Selected")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    country_address = models.ForeignKey(Country, verbose_name="Country", on_delete=models.CASCADE)
    city_address = models.ForeignKey(City, on_delete=models.CASCADE)
    address = models.CharField(verbose_name=_("Address Line"), help_text=_("Required"), max_length=255)
    phone = models.CharField(max_length=14, null=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False) 

    class Meta:
        ordering = ("-created",)
    
    def __str__(self):
        return (self.user.full_name + (' - ') + self.city_address)

class Booking(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    name = models.CharField(verbose_name=_('name'), max_length=250)
    address = models.CharField(verbose_name=_('billing_address'), max_length=250)
    email = models.EmailField(verbose_name=_('email'))
    type = models.CharField(max_length=250)
    phone = models.CharField(max_length=250)
    date = models.DateField()
    dateConfirm = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('booking_detail', kwargs={'id': self.pk})

class BookingServices(models.Model):
    parent = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="booking_items")
    service = models.ForeignKey(Elements, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
           
class Wallet(models.Model):
    WALLET = {
        ('Zelle','Zelle'),
        ('Paypal','Paypal'),
        ('Binance','Binance'),
    }
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, verbose_name=_('Type of Wallet'), choices=WALLET)
    email = models.EmailField(_('email'), unique=True)
    
    def __str__(self):
        return self.type + (' ') + self.user.username

class SendMoney(models.Model):
    STATUS = {
        ('Completed',_('Completed')),
        ('Pending',_('Pending')),
    }
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    ipadress = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS, default='Pending') 

    def __str__(self):
        return self.date

class PaypalClient(models.Model):
      def __init__(self):
        self.client_id = "AfA3d0-CCazeqNdk2AF_SSVdTLp0Eirwt-ku1rJsf-PcQMct4y3SCoeGyfYDj-nNI50v8EVtjr8OZ4q3"
        self.client_secret = "EAhV7gKAbyoFjnN-Lw_40nbyV1xdei2yJHqRXUp-Mc6yA0j5fJNUfROtEx_Cz0oL_tvSdxxyeNO4DdaB"
        self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(self.environment)

class UserMessages(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_messages', verbose_name=_('User'))
    subject = models.CharField(max_length=60, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Messages'))
    created = models.DateTimeField(auto_now_add=True)
    
    def get_absolute_url(self):
        return reverse('message-detail', kwargs={'pk': self.pk})
    
#Support
class Support(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_support', verbose_name=_('User'))
    email = models.EmailField()
    content = models.TextField(verbose_name=_('Brief description'))
    option = models.CharField(max_length=250, verbose_name=_('Subject'))
    image = models.ImageField(upload_to='cases/', blank=True, null=True, verbose_name=_("Image (optional)"))
    ticket = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ('open', 'Open'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed')
        ),
        default='in_progress',
    )

    def __str__(self):
        return self.option
    
    def get_absolute_url(self):
        return reverse('support-case', kwargs={'id': self.pk})
    
    def save(self, *args, **kwargs):
        if not self.ticket:
            self.ticket = get_random_string(length=10)
        super(Support, self).save(*args, **kwargs)
    
class ChatSupport(models.Model):
    case = models.ForeignKey(Support, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_user', null=True, blank=True)
    superuser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_superuser', null=True, blank=True)
    content = models.TextField(verbose_name='Answer', null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.response

#Site
class Content(models.Model):
    STATUS = (
        ('Publish', _('Publish')),
        ('Draft', _('Draft')),
    )
    CHOICES = (
        ('Communications', _('Communications')),
        ('Sweet Content', _('Sweet Content')),
        ('Marketing', _('Marketing')),
        ('Users Control', _('Users Control')),
        ('Fintech', _('Fintech')),
        ('Inventory', _('Inventory')),
        ('Operations', _('Operations')),
        ('Maintance', _('Maintance')),
        ('Speed', _('Speed')),
        ('Workflow', _('Workflow')),
        ('Support', _('Support')),
       
    )
    CHOICESPATH = (
        ('Stela Websites', _('Stela Websites')),
        ('Stela Business App', _('Stela Business App')),
        ('Services', _('Services')),
       
    )
    ABOUT = (
        ('Mission', _('Mission')),
        ('Vision', _('Vision')),
        ('Values', _('Values')),
       
    )
    CARD_OPTION = {
        ('card-tale',_('card-tale')),
        ('card-dark-blue',_('card-dark-blue')),
        ('card-light-blue',_('card-light-blue')),
        ('card-light-danger',_('card-light-danger')),
    }
    CATEGORY = {
        (_('News'),_('News')),
        (_('Advices'),_('Advices')),
        (_('Events'),_('Events')),
        (_('Stories'),_('Stories')),
        (_('Interviews'),_('Interviews')),
        (_('Resources'),_('Resources')),
    }
    category = models.CharField(max_length=100, choices=CATEGORY, blank=True, default=_('News'))
    card = models.CharField(max_length=50, null=True, choices=CARD_OPTION, verbose_name=_('Color Card'), blank=True)
    about = models.CharField(max_length=60, choices=ABOUT, verbose_name=_('Title'), null=True, blank=True, default='Mission')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author", null=True)
    section = models.CharField(max_length=200, verbose_name=_('Section'), default="No section")
    path = models.CharField(max_length=60, choices=CHOICESPATH, verbose_name=_('Path Title'), null=True)
    appstela = models.CharField(max_length=60, choices=CHOICES, verbose_name=_('App Title'), null=True)
    parent = models.ForeignKey(TemplateSections, related_name="template", on_delete=models.CASCADE, null=True, verbose_name=_("Parent"))
    tag = models.CharField(max_length=100, verbose_name=_('Tag'), null=True)
    status = models.CharField(max_length=10, choices=STATUS, null=True, verbose_name=_('Status'), blank=True, default='Draft')
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    media = models.FileField(upload_to='media/', blank=True, null=True)
    video = models.FileField(upload_to='video/', blank=True, null=True)
    folder_doc = models.FileField(upload_to='bucket/', null=True, blank=True)
    subtitle = models.CharField(max_length=250, verbose_name=_('Subtitle'), null=True, blank=True)
    content = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, help_text=_("Required"))
    lang = models.CharField(max_length=80, default="en")
    url = models.CharField(max_length=100, verbose_name='url', null=True)
    site = models.CharField(max_length=100, verbose_name=_("Website"), null=True)
    schedule = models.DateTimeField(null=True, blank=True)
    is_schedule = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Content, self).save(*args, **kwargs)

    def image_tag(self):
        if self.media.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.media.url))
        else:
            return ""
        
    def mp4(self):
        return self.media.name.endswith('.mp4')
    
    def get_absolute_url(self):
        return reverse('home:blog_detail', kwargs={'pk': self.pk, 'slug': self.slug})

class SiteControl(models.Model):
    ip=models.CharField(max_length=60)
    lon=models.CharField(max_length=100)
    lat=models.CharField(max_length=100)
    dateview=models.DateTimeField(auto_now_add=True)
    pishing=models.BooleanField(default=False)

class SiteViews(models.Model):
    blog=models.ForeignKey(Content, on_delete=models.CASCADE, null=True)
    host=models.CharField(max_length=150, default='no catch data')
    page=models.CharField(max_length=150, default='page no catched') 
    views=models.IntegerField(default=0)
    country=models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.CASCADE, null=True)
    lastdate=models.CharField(max_length=150, default='no catch data')
    created=models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

    def __str__(self):
        return self.host + (' ') + self.lastdate

class FAQ(models.Model):
    POST_STATUS_CHOICES=(
        ('Draft',_('Draft')),
        ('Publish',_('Publish'))
    )
    LEGAL_CHOICES=(
        (_('Product/Service'),_('Product/Service')),
        (_('Technical Support'),_('Technical Support')),
        (_('Purchasing Process'),_('Purchasing Process')),
        (_('General Inquiries'),_('General Inquiries')),
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author_faq")
    status = models.CharField(max_length=10, choices=POST_STATUS_CHOICES, verbose_name=_('Status'), default="Draft")
    legal = models.CharField(max_length=28, choices=LEGAL_CHOICES, verbose_name=_('Legal'), default="shipping")
    lang = models.CharField(max_length=80, default="en")
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

    def __str__(self):
        return self.created
    
class SetFaq(models.Model):
    faq=models.ForeignKey(FAQ, on_delete=models.CASCADE, null=True, related_name='set_faq')
    question = models.CharField(max_length=250, verbose_name=_('Question'), default='')
    answer = models.TextField()
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

    def __str__(self):
        return self.created

class Notifications(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, default="No Read")
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    section = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.section + (' - ') + self.user.full_name)

class Comments(models.Model):
    POST_STATUS_CHOICES=(
        ('Publish', _('Publish')),
        ('Draft', _('Draft')),
    )
    post = models.ForeignKey(Content, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=150, verbose_name=_('Name'))
    email = models.EmailField(verbose_name='Email')
    status = models.CharField(max_length=10, choices=POST_STATUS_CHOICES, default="Draft") 
    lang = models.CharField(max_length=80)
    message = models.TextField(verbose_name=_('Message'))

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        self.message = caption_optimizer(self.message)
        super(Comments, self).save(*args, **kwargs)

class FormsetFAQ(models.Model):
    faq = models.ForeignKey(FAQ, related_name="fitems", on_delete=models.CASCADE)
    question = models.CharField(max_length=150, blank=False, verbose_name=_("Questions"))
    response = models.TextField(verbose_name=_("Answer"))

class ImageGallery(models.Model): 
    parent = models.ForeignKey(Content, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name=_("Image"), upload_to='gallery/')

class DynamicBullets(models.Model):
    parent = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='bullet_content', null=True)
    icon = models.CharField(max_length=250, verbose_name=_('Icon'), blank=True, null=True)
    percentaje = models.IntegerField(default=0, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    bullet_title = models.CharField(max_length=250, verbose_name=_('Bullet Title'), null=True)
    content_bullet = models.TextField(null=True, verbose_name=_('Content Bullet'))

    def __str__(self):
        return self.bullet_title

class PetData(models.Model):
    FAMILY=(
        ('Dog',_('Dog')),
    )
    WEIGHT =(
        ('1 to 10','1 to 10'),
        ('10 to 25','10 to 25'),
        ('26 to 40','26 to 40'),
        ('41 to 70','41 to 70'),
        ('71 to 91','71 to 91'),
        ('91 +','91 +'),
    )
    BREEDS =(
        ('Short Coat Breeds',_('Short Coat Breeds')),
        ('Wire Coat Breeds',_('Wire Coat Breeds')),
        ('Soft Coat Breeds',_('Soft Coat Breeds')),
        ('Double Coat Breeds',_('Double Coat Breeds')),
        ('Doodles Breeds',_('Doodles Breeds'))
    )

    parent = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="pet_service", null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pet_owner')
    name = models.CharField(max_length=100, verbose_name=_("Pet's name"))
    image = models.ImageField(verbose_name=_("Image"), upload_to='images/')
    family = models.CharField(max_length=10, choices=FAMILY, verbose_name=_("Pet Family"), help_text=_("Choose Please"))
    allergy = models.BooleanField(verbose_name=_("It's Allergic?"), default=False)
    reactive = models.CharField(max_length=250, verbose_name=_("Product React"), blank=True, null=True)
    weight = models.CharField(max_length=40, choices=WEIGHT, verbose_name=_("Weght LBS"), help_text=_("Choose Please"))
    breed = models.CharField(max_length=80, choices=BREEDS, verbose_name=_("Pet Breed"), help_text=_("Choose Please"))
    price = models.DecimalField(verbose_name=_("Regular price USD"), help_text=_("Maximun 999.99"), null=True, blank=True, error_messages={
        "name": {
            "max_lenght": _("The price must be between 0 and 999.99"),
        },
    },
    max_digits=5,
    decimal_places=2,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, editable=False)
    
    def __str__(self):
        return self.name

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""
        
class SitePolicy(models.Model):
    SECTION ={
        ('Privacy Policy', _('Privacy Policy')),
        ('Cookie Policy', _('Cookie Policy')),
        ('Terms and Conditions', _('Terms and Conditions')),
        ('Return Policy', _('Return Policy')),
        ('Disclaimer', _('Disclaimer')),
    }
    STATUS = (
        ('Publish', _('Publish')),
        ('Draft', _('Draft')),
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="site_docs")
    title = models.CharField(max_length=150, null=True, verbose_name=_('Title'), blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="Draft", verbose_name=_('Status'), blank=True)
    section = models.CharField(max_length=150, blank=True, choices=SECTION, default="Terms and Conditions") 
    lang = models.CharField(max_length=80, default="en")
    created = models.DateTimeField(auto_now_add=True)

class LegalProvision(models.Model):
    policy = models.ForeignKey(SitePolicy, related_name='content', on_delete=models.CASCADE) 
    clause = models.CharField(max_length=150, blank=False, verbose_name=_('Clause'))
    clause_content = models.TextField(verbose_name=_('Content'), blank=True)
    created = models.DateTimeField(auto_now_add=True) 

#MetaPlattforms
class FacebookPage(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fans=models.IntegerField(default=0)
    followers=models.IntegerField(default=0)
    name=models.CharField(max_length=250)
    category=models.CharField(max_length=250)
    asset_id=models.CharField(max_length=50, default='noid')
    token=models.CharField(max_length=250, default='not_token')
    image=models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.owner + (' ') + self.name

class FacebookPostPage(models.Model):
    page=models.ForeignKey(FacebookPage, on_delete=models.CASCADE, related_name="page")
    feed_id=models.CharField(max_length=500, default='noid', blank=True)
    content=models.TextField()
    schedule=models.DateTimeField(null=True, blank=True)
    is_video=models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def get_video_url(self):
        if self.video:
            return self.video.url
        return None
    
    def __str__(self):
        return self.owner.full_name + _('Facebook Post')

class FacebookPostMedia(models.Model):
    post=models.ForeignKey(FacebookPostPage, on_delete=models.CASCADE)
    media=models.FileField(upload_to='fb_media/', null=True, blank=True)

    def get_image_url(self):
        if self.media:
            return self.media.url
        return None

class FacebookPageEvent(models.Model):
    TYPE = (
                ('', _('Select Type')),
                ('private', _('Private')),
                ('public', _('Public')),
                ('group', _('Group')),
                ('community', _('Community')),
                ('friends', _('Friends')),
                ('work_company', _('Work Company')),          
    )
    STATUS = (
                ('active', _('Scheduled')),
                ('is_canceled', _('Cancel Event')),
                ('is_draft', _('Draft')),
                ('is_online', _('Online')),
    )
    CHOICES = (
                ('', _('Select Category')),
                ('CLASSIC_LITERATURE', _('Classic Literature')),
                ('COMEDY', _('Comedy')),
                ('CRAFTS', _('Crafts')),
                ('DANCE', _('Dance')),
                ('DRINKS', _('Drinks')),
                ('FITNESS_AND_WORKOUTS', _('Fitness & Workouts')),
                ('FOODS', _('Foods')),
                ('GAMES,', _('Games')),
                ('GARDENING', _('Gardening')),
                ('HEALTH_AND_MEDICAL', _('Health & Medical')),
                ('HEALTHY_LIVING_AND_SELF_CARE', _('Healthy Living & Self Care')),
                ('HOME_AND_GARDEN', _('Home & Garden')),
                ('MUSIC_AND_AUDIO', _('Music & Audio')),
                ('PARTIES', _('Parties')),
                ('PROFESSIONAL_NETWORKING', _('Professional Networking')),
                ('RELIGIONS', _('Religions')),
                ('SHOPPING_EVENT', _('Shopping Event')),
                ('SOCIAL_ISSUES', _('Social Issues')),
                ('SPORTS', _('Sports')),
                ('THEATER', _('Theater')),
                ('TV_AND_MOVIES', _('Tv & Movies')),
                ('VISUAL_ARTS', _('Visual Arts')),
    )
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_owner")
    status=models.CharField(max_length=80, choices=STATUS, default=_("Select Type"))
    type=models.CharField(max_length=80, choices=TYPE, default=_("Scheduled"))
    category=models.CharField(max_length=80, choices=CHOICES, default=_("Select Category"))
    page=models.ForeignKey(FacebookPage, on_delete=models.CASCADE, related_name="events", null=True, blank=True)
    name=models.CharField(max_length=250)
    lang = models.CharField(max_length=80, default="en")
    start_time=models.DateField()
    location=models.CharField(max_length=250, default=_("No location selected"))
    description=models.TextField(blank=True)
    cover=models.ImageField(upload_to='events/')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.page.name + (' ') + self.name
    
    def get_url(self):
        if self.cover:
            return self.cover.url
        return None

class FacebookPageConversations(models.Model):
    page=models.ForeignKey(FacebookPage, on_delete=models.CASCADE, related_name="conversations", null=True, blank=True)
    core_id=models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.owner.full_name + (' ') + self.core_id

class FacebookPageMessages(models.Model):
    conversation=models.ForeignKey(FacebookPageConversations, on_delete=models.CASCADE)
    from_message=models.CharField(max_length=250)
    to_message=models.CharField(max_length=250)
    message=models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.conversation

class FacebookPageShares(models.Model):
    post=models.ForeignKey(FacebookPostPage, on_delete=models.CASCADE)
    from_user=models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.from_user + _('Page Share')

class FacebookPageLikes(models.Model):
    post=models.ForeignKey(FacebookPostPage, on_delete=models.CASCADE)
    from_user=models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.from_user + _('Page Likes')

class FacebookPageComments(models.Model):
    post=models.ForeignKey(FacebookPostPage, on_delete=models.CASCADE)
    from_user=models.CharField(max_length=250)
    from_user_id=models.CharField(max_length=500)
    comment=models.CharField(max_length=2000)
    comment_id=models.CharField(max_length=500)
    created=models.DateTimeField(auto_now_add=True)
    update_rate=models.DateTimeField(default=datetime.now() + timedelta(hours=1))

    def __str__(self):
        return self.from_user + self.post.feed_id

class FacebookPageCommentsReply(models.Model):
    comment=models.ForeignKey(FacebookPageComments, on_delete=models.CASCADE)
    from_user=models.CharField(max_length=250)
    comment=models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.from_user + self.comment.core_id

class FacebookPageImpressions(models.Model):
    page=models.ForeignKey(FacebookPage, on_delete=models.CASCADE, related_name="impressions")
    qty=models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.page.owner.full_name + " - " + self.page.name

class InstagramAccount(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    commerce_id=models.CharField(max_length=250, default="no_commerce")
    followers=models.IntegerField(default=0)
    title=models.CharField(max_length=250)
    username=models.CharField(max_length=250)
    asset_id=models.CharField(max_length=50, default='noid')
    image=models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class IGPost(models.Model):
    STATUS = (
                ('publish', _('Publish')),
                ('draft', _('Draft')),
    )
    MEDIATYPE = (
                ('POST', _('POST')),
                ('REELS', _('Reels')),
                ('CAROUSEL', _('Carousel')),
                ('STORIES', _('Stories')),         
    )
    parent=models.ForeignKey(InstagramAccount, on_delete=models.CASCADE, related_name="media")
    container_id=models.CharField(max_length=500, default='noid', blank=True)
    feed_id=models.CharField(max_length=500, default='noid', blank=True)
    token=models.CharField(max_length=500, default='empty', blank=True)
    publish_status=models.CharField(max_length=500, default='noid', blank=True)
    status=models.CharField(max_length=80, choices=STATUS, default=_("draft"), blank=True)
    mediatype=models.CharField(max_length=80, choices=MEDIATYPE, default=_("Post"),blank=True)
    caption=models.TextField(blank=True)
    audioname=models.CharField(max_length=500, default='Original Audio', blank=True)
    schedule=models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.parent.asset_id
    
    def save(self, *args, **kwargs):
        if not self.schedule:
            self.schedule = timezone.get_current_timezone_name()
        super().save(*args, **kwargs)

class IGMediaContent(models.Model):
    post=models.ForeignKey(IGPost, on_delete=models.CASCADE, related_name="igitem", null=True, blank=True)
    media=models.FileField(upload_to='igmedia/', null=True, blank=True)
    cover=models.FileField(upload_to='igcover/', null=True, blank=True)

    def get_url(self):
        if self.media:
            return self.media.url
        return None
    
    def get_cover(self):
        if self.cover:
            return self.cover.url
        return None
    
    def mp4(self):
        return self.media.name.endswith('.mp4')
    
    def image_tag(self):
        if self.media.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.media.url))
        else:
            return ""
        
    def cover_tag(self):
        if self.cover.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.cover.url))
        else:
            return ""

class IGUserTag(models.Model):
    post=models.ForeignKey(IGPost, on_delete=models.CASCADE, null=True, blank=True)
    igname=models.CharField(max_length=200, default='noid', blank=True)

class IGCarouselMetric(models.Model):
    post=models.ForeignKey(IGPost, on_delete=models.CASCADE, null=True, blank=True, related_name="metric_carousel")
    album_engagement=models.IntegerField(default=0, blank=True)
    album_impressions=models.IntegerField(default=0, blank=True)
    album_reach=models.IntegerField(default=0, blank=True)
    album_saved=models.IntegerField(default=0, blank=True)
    album_video_views=models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.post.feed_id + ' ' + 'Carousel Metric'

class IGPostMetric(models.Model):
    post=models.ForeignKey(IGPost, on_delete=models.CASCADE, null=True, blank=True, related_name="metric_post")
    engagement=models.IntegerField(default=0, blank=True)
    impressions=models.IntegerField(default=0, blank=True)
    reach=models.IntegerField(default=0, blank=True)
    saved=models.IntegerField(default=0, blank=True)
    video_views=models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.post.feed_id + ' ' + 'Post Metric'

class IGReelMetric(models.Model):
    post=models.ForeignKey(IGPost, on_delete=models.CASCADE, null=True, blank=True, related_name="metric_reel")
    comments=models.IntegerField(default=0, blank=True)
    likes=models.IntegerField(default=0, blank=True)
    plays=models.IntegerField(default=0, blank=True)
    reach=models.IntegerField(default=0, blank=True)
    saved=models.IntegerField(default=0, blank=True)
    shares=models.IntegerField(default=0, blank=True)
    total_interactions=models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.post.feed_id + ' ' + 'Reels Metric'

class IGStoriesMetric(models.Model):
    post=models.ForeignKey(IGPost, on_delete=models.CASCADE, null=True, blank=True, related_name="metric_stories")
    exits=models.IntegerField(default=0, blank=True)
    impressions=models.IntegerField(default=0, blank=True)
    replies=models.IntegerField(default=0, blank=True)
    taps_forward=models.IntegerField(default=0, blank=True)
    taps_back=models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.post.feed_id + ' ' + 'Stories Metric'
    
#googlePlattforms
class YouTubeToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='youtube_token')
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=50)
    expires_in = models.DateTimeField()
    scope = models.TextField()

    def __str__(self):
        return f'YouTube Token for {self.user.username}'
    
#siteModels
class LiteraryWork(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="literary_author")
    publication_date = models.DateField()
    genre = models.CharField(max_length=50)
    synopsis = models.TextField()

    def __str__(self):
        return self.title

class Resource(models.Model):
    STATUS = (
        ('publish', _('Publish')),
        ('draft', _('Draft')),
    )
    status=models.CharField(max_length=80, choices=STATUS, default=_("draft"), blank=True)
    category = models.CharField(max_length=255, verbose_name='Resource Category')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/')  
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def is_excel(self):
        _, file_extension = os.path.splitext(self.file.name)
        return file_extension in ['.xls', '.xlsx']

    def is_pdf(self):
        _, file_extension = os.path.splitext(self.file.name)
        return file_extension.lower() == '.pdf'
    
class BillFile(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='facturas/')
    upload_date = models.DateTimeField(default=timezone.now)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"Factura de {self.client.username}: {self.title}"

class Club(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Discussion(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    starter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class APIStelaClient(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_client")
    client_key = models.CharField(max_length=255, unique=True)
    secret_key = models.CharField(max_length=255)
    is_subscriber = models.BooleanField(default=False)

    def __str__(self):
        return self.owner.email

#StelaControl
class ProStelaExpert(models.Model):
   owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner_proexpert")
   model = models.CharField(max_length=80) 
   created = models.DateTimeField(auto_now_add=True)

   def __str__(self):
        return self.owner.username + str(' ') + str(self.model)
   
   class Meta:
    unique_together = ('owner', 'model')

class ProStelaData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='prostela')
    title = models.CharField(max_length=150, default="No title")
    chatbox = models.TextField(default="Empty")
    storage_data = models.TextField(default="Empty")
    response_time = models.DecimalField(max_digits=6, decimal_places=2)
    section = models.CharField(max_length=150, default="custom")
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.full_name + ' ' + str(self.created)
    
class ProStelaUsage(models.Model):
    prompt = models.ForeignKey(ProStelaData, on_delete=models.CASCADE, related_name="prompt_data")
    tokens = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

class DataEmail(models.Model):
    email=models.EmailField(null=False, unique=False)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Newsletter(models.Model):
    STATUS = {
        ('Draft','Draft'),
        ('Send','Send'),
    }
    
    OPTION ={
        ('Style Template 1',_('Style Template 1')),
        ('Style Template 2',_('Style Template 2')),
        ('Style Template 3',_('Style Template 3')),
        ('Style Template 4',_('Style Template 4')),
    }
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lead")
    template = models.CharField(max_length=60, choices=OPTION, verbose_name=_('Style'), null=True)
    subject = models.CharField(max_length=250, verbose_name='Subject')
    body = models.TextField(verbose_name='Messages')
    email = models.ManyToManyField(DataEmail, verbose_name='Emails')
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS)

class JobApplication(models.Model):
    CHOICES = (
                ('', _('Choose One')),
                ('Part-Time', _('Part-Time')),
                ('Full-Time', _('Full-Time')),
                ('Internship', _('Internship')),
                ('Freelance', _('Freelance')),

        )
    first_name = models.CharField(max_length=50, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last Name"))
    email = models.EmailField(verbose_name=_("Email Address"))
    phone = models.CharField(max_length=15, verbose_name=_("Phone Number"))
    address = models.CharField(max_length=300,verbose_name=_("Address"))
    cv = models.FileField(upload_to='cv/', blank=True, null=True, verbose_name=_("Upload CV"))
    position_applied = models.CharField(max_length=100, verbose_name=_("Position Applied For"))
    salary_expectations = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Salary Expectations"))
    availability = models.CharField(max_length=100, choices=CHOICES, default=(_('Choose One')))
    comments = models.TextField(verbose_name=_("Additional Comments"), blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position_applied}"

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"

class EmploymentHistory(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='employment_history')
    employer = models.CharField(max_length=100, verbose_name=_("Employer"))
    job_title = models.CharField(max_length=100, verbose_name=_("Job Title"))
    employment_period_from = models.DateField(verbose_name=_("Employment Period From"))
    employment_period_to = models.DateField(verbose_name=_("Employment Period To"), blank=True, null=True)
    description = models.TextField(verbose_name=_("Job Description"), blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.employer}"

class Education(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='education')
    institution_name = models.CharField(max_length=100, verbose_name=_("Institution Name"))
    degree_obtained = models.CharField(max_length=100, verbose_name=_("Degree Obtained"), blank=True, null=True)
    study_period_from = models.DateField(verbose_name=_("Study Period From"), blank=True, null=True)
    study_period_to = models.DateField(verbose_name=_("Study Period To"), blank=True, null=True)
    description = models.TextField(verbose_name=_("Description of Study"), blank=True, null=True)

    def __str__(self):
        return self.institution_name

class Reference(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='references')
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    contact_info = models.TextField(verbose_name=_("Contact Information"))
    relationship = models.CharField(max_length=100, verbose_name=_("Relationship"), blank=True, null=True)

    def __str__(self):
        return self.name

class InvoiceFile(models.Model):
    STATUS=(
        ('pending',_('Pending')),
        ('checked', _('Checked'))
    )
    status = models.CharField(max_length=10, choices=STATUS, default="Pending")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='invoice_files')
    legal_name = models.CharField(max_length=255, verbose_name=_('Legal Name'))
    control_id = models.CharField(max_length=255, verbose_name=_('Control Number'))
    pdf_file = models.FileField(upload_to='invoices/')
    date = models.DateField(verbose_name=_('Date'))
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invoice {self.id} - Legal Name {self.legal_name}'

class RetentionFile(models.Model):
    STATUS=(
        ('pending',_('Pending')),
        ('checked', _('Checked'))
    )
    status = models.CharField(max_length=10, choices=STATUS, default="Pending")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='retentions')
    legal_name = models.CharField(max_length=255, verbose_name=_('Legal Name'))
    control_id = models.CharField(max_length=255, verbose_name=_('Control ID'))
    pdf_file = models.FileField(upload_to='retentions/')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Retention {self.id} - Legal Name {self.legal_name}'

class BankStatement(models.Model):
    STATUS=(
        ('pending',_('Pending')),
        ('checked', _('Checked'))
    )
    status = models.CharField(max_length=10, choices=STATUS, default="Pending")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='bank_statements')
    bank_holder = models.CharField(max_length=255, verbose_name=_('bank_holder'))
    bank = models.CharField(max_length=255, verbose_name=_('bank'))
    pdf_file = models.FileField(upload_to='bank_statements/')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Bank Statement {self.id} - User {self.user.username}'

class TaxReturn(models.Model):
    STATUS=(
        ('draft',_('Draft')),
        ('publish', _('Publish'))
    )
    status = models.CharField(max_length=10, choices=STATUS, default="Pending")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='tax_returns')
    business = models.CharField(max_length=255, verbose_name=_('Legal Name'))
    type = models.CharField(max_length=255, verbose_name=_('Type'))
    date = models.DateField(verbose_name=_('Date'))
    pdf_file = models.FileField(upload_to='tax_returns/')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Tax Return {self.id} - Business {self.legal_name}'

class TaxID(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='tax_id')
    number_id = models.CharField(max_length=255, verbose_name=_('Number ID'))
    pdf_file = models.FileField(upload_to='taxID/', verbose_name=_('Business ID'))
    pdf_file2 = models.FileField(upload_to='taxID/', verbose_name=_('Articles of Organization'))
    created = models.DateTimeField(auto_now_add=True)
