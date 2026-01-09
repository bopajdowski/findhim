from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
import uuid
from django.db.models import UUIDField


class DaneOperator1(models.Model):
    import_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    poczatek = models.DateTimeField(null=True, blank=True)  # początek rozmowy/sms/transmisji
    koniec = models.DateTimeField(null=True, blank=True)    # koniec rozmowy/transmisji
    czas = models.IntegerField(null=True, blank=True)       # czas trwania w sekundach
    msisdn1 = models.CharField(max_length=20, null=True, blank=True)
    imei1 = models.CharField(max_length=20, null=True, blank=True)
    kierunek = models.CharField(max_length=50, null=True, blank=True)
    msisdn2 = models.CharField(max_length=20, null=True, blank=True)
    imei2 = models.CharField(max_length=20, null=True, blank=True)
    typ = models.CharField(max_length=20, null=True, blank=True)  # SMS, rozmowa, internet itp.
    rodzaj = models.CharField(max_length=20, null=True, blank=True)
    bts1 = models.CharField(max_length=100, null=True, blank=True)  # adres BTSa
    bts2 = models.CharField(max_length=100, null=True, blank=True)
    lac1 = models.FloatField(null=True, blank=True)
    cid1 = models.FloatField(null=True, blank=True)
    wspolrzedne1 = gis_models.PointField(null=True, blank=True, srid=4326)  # Szer. geogr., d. geogr. 1 (parsuj '51.1406,16.9439')
    azymut1 = models.IntegerField(null=True, blank=True)  # max 360
    kt1 = models.IntegerField(null=True, blank=True)       # max 360
    zasig1 = models.FloatField(null=True, blank=True)      # w metrach
    mcc1 = models.FloatField(null=True, blank=True)
    mnc1 = models.FloatField(null=True, blank=True)
    lac2 = models.FloatField(null=True, blank=True)
    cid2 = models.FloatField(null=True, blank=True)
    wspolrzedne2 = gis_models.PointField(null=True, blank=True, srid=4326)
    azymut2 = models.IntegerField(null=True, blank=True)
    kt2 = models.IntegerField(null=True, blank=True)
    zasig2 = models.FloatField(null=True, blank=True)
    mcc2 = models.FloatField(null=True, blank=True)
    mnc2 = models.FloatField(null=True, blank=True)
    imsi1 = models.CharField(max_length=20, null=True, blank=True)
    imsi2 = models.CharField(max_length=20, null=True, blank=True)
    przekierowanie = models.CharField(max_length=50, null=True, blank=True)
    przekier_imei = models.CharField(max_length=50, null=True, blank=True)
    przekier_imsi = models.CharField(max_length=50, null=True, blank=True)
    przekier_bts = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'dane_operator1'
        verbose_name = 'Dane Operator1'
        verbose_name_plural = 'Dane Operator1'
