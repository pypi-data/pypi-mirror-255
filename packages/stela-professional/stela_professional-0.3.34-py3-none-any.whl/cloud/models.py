from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.
class Domains(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="domainowner", null=True)
    status = models.CharField(max_length=150, default="Pending")
    name = models.CharField(max_length=150)
    tld = models.CharField(max_length=150)
    price = models.DecimalField(blank=True, null=True, verbose_name=_("Price USD"), help_text=_("Maximun 9999.99"), error_messages={
        "name": {
            "max_lenght": _("The price must be between 0 and 9999.99"),
        },
    },
    max_digits=6,
    decimal_places=2,
    )
    request = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

    def __str__(self):
        return self.name + '.' + self.tld

class VirtualCloud(models.Model):
    domain = models.ForeignKey(Domains, on_delete=models.CASCADE, null=True, related_name="vdomain")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="virtualcloud", null=True)
    module = models.CharField(max_length=400)
    status = models.CharField(max_length=150, blank=False, default="Turn Off")
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

class ZoneDNS(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="zone", null=True)
    module = models.CharField(max_length=400)
    domain = models.ForeignKey(Domains, on_delete=models.CASCADE, null=True, related_name="domain")
    status = models.CharField(max_length=150, blank=False, default="Turn Off")
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

class CloudStorage(models.Model):
    domain = models.ForeignKey(Domains, on_delete=models.CASCADE, null=True, related_name="storage")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cloudstorage", null=True)
    module = models.CharField(max_length=400)
    status = models.CharField(max_length=150, blank=False, default="Turn Off")
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

class ResquetsCloud(models.Model):
    domain = models.ForeignKey(Domains, on_delete=models.CASCADE, null=True, related_name="recloud")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requestcloud", null=True)
    module = models.CharField(max_length=400)
    status = models.CharField(max_length=150, blank=False, default="Turn Off")
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)

class UsageCloud(models.Model):
    virtualcloud = models.ForeignKey(VirtualCloud, on_delete=models.CASCADE, related_name="virtual_usage", null=True)
    zonadns = models.ForeignKey(ZoneDNS, on_delete=models.CASCADE, related_name="dns_usage", null=True)
    cloudstorage = models.ForeignKey(CloudStorage, on_delete=models.CASCADE, related_name="storage_usage", null=True)
    requestcloud = models.ForeignKey(ResquetsCloud, on_delete=models.CASCADE, related_name="request_usage", null=True)
    usage = models.IntegerField(default=1)
    monthy_cost = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    created = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)