from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
# Create your models here.

class transportermodel(models.Model):
    trans=models.CharField(max_length=20,primary_key=True)

    def __str__(self):
        return self.trans

class partymodel(models.Model):
    party=models.CharField(max_length=50,primary_key=True)
    add = models.CharField(max_length=50)

    def __str__(self):
        return self.party

class placemodel(models.Model):
    place=models.CharField(max_length=20,primary_key=True)

    def __str__(self):
        return self.place

class shiftmodel(models.Model):
    trip = models.CharField(max_length=20,primary_key=True)

    def __str__(self):
        return self.trip

class drivermodel(models.Model):
    driver = models.CharField(max_length=20,primary_key=True)


    def __str__(self):
        return self.driver

class truckmodel(models.Model):
    code=models.CharField(max_length=20,primary_key=True)
    trans = models.ForeignKey(transportermodel, on_delete=models.CASCADE, default="")
    feet=models.IntegerField()
    driver = models.ForeignKey(drivermodel, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.code

class tripmodel(models.Model):
    code = models.ForeignKey(truckmodel, on_delete=models.CASCADE, null=True, blank=True)
    driver = models.ForeignKey(drivermodel, on_delete=models.CASCADE, null=True, blank=True)
    dat = models.CharField(max_length=20, verbose_name='Date')
    dis = models.FloatField(verbose_name='Distance')
    disqnt = models.FloatField(verbose_name='Distance Quantity')
    cont = models.CharField(max_length=50, verbose_name='Container')
    buy = models.IntegerField(default=0, verbose_name='Buy')
    party = models.ForeignKey(partymodel, on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey(placemodel, on_delete=models.CASCADE, null=True, blank=True)
    trip = models.ForeignKey(shiftmodel, on_delete=models.CASCADE, null=True, blank=True)
    checked = models.BooleanField(verbose_name='Checked', default=False)
    update = models.BooleanField(verbose_name='Update Check', default=False)
    bill = models.BooleanField(verbose_name='Bill Check', default=False)
    bno = models.IntegerField(verbose_name='Bill Number')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tripmodel_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tripmodel_updated')
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='tripmodel_deleted')
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(table_name='tripmodel_history')
    amount = models.FloatField(default=0.0)
    sheetno=models.IntegerField(default=0)
    opkm = models.IntegerField(default=0)
    clkm = models.IntegerField(default=0)
    battaid=models.IntegerField(default=0)
    halt=models.IntegerField(default=0)
    hire = models.IntegerField(default=0)
    exptotal=models.IntegerField(default=0)
    expid=models.IntegerField(default=0)
    com=models.IntegerField(default=0)
    outadv=models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'

class billmodel(models.Model):
    bno =  models.IntegerField(primary_key=True)
    bdate = models.CharField(max_length=20,default='')
    hire = models.IntegerField(default=0)
    toll = models.IntegerField(default=0)
    unload = models.IntegerField(default=0)
    enblock = models.IntegerField(default=0)
    shift = models.IntegerField(default=0)
    weigh = models.IntegerField(default=0)
    halt = models.IntegerField(default=0)
    diesel = models.FloatField(default=0.0)
    hireqnt = models.IntegerField(default=0)
    tollqnt = models.IntegerField(default=0)
    unloadqnt = models.IntegerField(default=0)
    enblockqnt = models.IntegerField(default=0)
    shiftqnt = models.IntegerField(default=0)
    weighqnt = models.IntegerField(default=0)
    haltqnt = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='billmodel_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='billmodel_updated')
    updated_at = models.DateTimeField(auto_now=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='billmodel_deleted')
    history = HistoricalRecords(table_name='billmodel_history')
    total = models.FloatField(default=0.0)



class battamodel(models.Model):
    sheetno=models.IntegerField()
    date=models.CharField(max_length=20,default='')
    code = models.ForeignKey(truckmodel, on_delete=models.CASCADE, default="")
    driver = models.ForeignKey(drivermodel, on_delete=models.CASCADE, default="")
    batta=models.IntegerField(default=0)
    lift=models.IntegerField(default=0)
    print = models.IntegerField(default=0)
    othexp = models.IntegerField(default=0)
    wei = models.IntegerField(default=0)
    halt = models.IntegerField(default=0)
    park = models.IntegerField(default=0)
    rto = models.IntegerField(default=0)
    adv = models.IntegerField(default=0)
    loan = models.IntegerField(default=0)
    total=models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='battamodel_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='battamodel_updated')
    updated_at = models.DateTimeField(auto_now=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='battamodel_deleted')
    history = HistoricalRecords(table_name='battamodel_history')

    def __str__(self):
        return self.sheetno


class expensemodel(models.Model):
    date = models.CharField(max_length=20, default='')
    code = models.ForeignKey(truckmodel, on_delete=models.CASCADE, default="")
    roro = models.IntegerField(default=0)
    adblue = models.IntegerField(default=0)
    oil = models.IntegerField(default=0)
    insur = models.IntegerField(default=0)
    tax = models.IntegerField(default=0)
    emi = models.IntegerField(default=0)
    test = models.IntegerField(default=0)
    work = models.IntegerField(default=0)
    spare = models.IntegerField(default=0)
    workshop = models.CharField(max_length=20,default='')
    rethread = models.IntegerField(default=0)
    tyre = models.IntegerField(default=0)
    toll = models.IntegerField(default=0)
    park = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='expensemodel_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='expensemodel_updated')
    updated_at = models.DateTimeField(auto_now=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='expensemodel_deleted')
    history = HistoricalRecords(table_name='expensemodel_history')

    def __str__(self):
        return self.code
