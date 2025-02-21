"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .import views

urlpatterns = [
    path('staffindex',views.staffindex,name="staffindex"),
    path('staffhome',views.staffhome,name="staffhome"),
    path('truckreg',views.truckreg,name="truckreg"),
    path('transporterreg', views.transporterreg, name="transporterreg"),
    path('party', views.party, name="party"),
    path('place', views.place, name="place"),
    path('driver', views.driver, name="driver"),
    path('shift', views.shift, name="shift"),
    path('triporder', views.triporder, name="triporder"),
    path('bill', views.bill, name="bill"),
    path('billdetails', views.billdetails, name="billdetails"),
    path('billpdf', views.billpdf, name="billpdf"),
    path('billupdate/<str:bno>', views.billupdate, name="billupdate"),
    path('', views.login, name="login"),
    path('register', views.register, name='register'),
    path('userview', views.userview, name='userview'),
    path('userdel/<str:username>', views.userdel, name="userdel"),
    path('dailyupdate', views.dailyupdate, name="dailyupdate"),
    path('adminhome', views.adminhome, name="adminhome"),
    path('outtriporder', views.outtriporder, name="outtriporder"),
    path('outdailyupdate', views.outdailyupdate, name="outdailyupdate"),
    path('batta/<str:id>', views.batta, name="batta"),
    path('battaupdate', views.battaupdate, name="battaupdate"),
    path('battaup/<str:id>', views.battaup, name='battaup'),
    path('battadel/<str:id>', views.battadel, name='battadel'),
    path('battaview', views.battaview, name="battaview"),
    path('expense/<str:id>', views.expense, name="expense"),
    path('expenseview', views.expenseview, name="expenseview"),
    path('expenseupdate', views.expenseupdate, name="expenseupdate"),
    path('expup/<str:id>/', views.expup, name='expup'),
    path('expdel/<str:id>/', views.expdel, name='expdel'),
    path('triporderupdate', views.triporderupdate, name="triporderupdate"),
    path('isaup/<str:id>/', views.isaup, name='isaup'),
    path('isadel/<str:id>/', views.isadel, name='isadel'),
    path('triphistory', views.triphistory, name='triphistory'),
    path('triporderhistory/<str:id>', views.triporderhistory, name="triporderhistory"),
    path('battahistory', views.battahistory, name='battahistory'),
    path('battaorderhistory/<str:id>', views.battaorderhistory, name="battaorderhistory"),
    path('expensehistory', views.expensehistory, name='expensehistory'),
    path('expenseorderhistory/<str:id>', views.expenseorderhistory, name="expenseorderhistory"),
    path('logout_view', views.logout_view, name='logout_view'),
    path('mileage', views.mileage, name="mileage"),
    path('isaprofit', views.isaprofit, name="isaprofit"),
    path('viewbill', views.viewbill, name="viewbill"),
    path('billing', views.billing, name="billing"),
    path('delrow/<id>', views.delrow, name='delrow'),
    path('billhistory', views.billhistory, name="billhistory"),
    path('billorderhistory/<str:id>', views.billorderhistory, name="billorderhistory"),
    path('staffbattaview', views.staffbattaview, name="staffbattaview"),
    path('staffexpview', views.staffexpview, name="staffexpview"),
    path('stafftripview', views.stafftripview, name="stafftripview"),
    path('vehicle', views.vehicle, name="vehicle"),
    path('adminvehicle', views.adminvehicle, name="adminvehicle"),
    path('outtriporderupdate', views.outtriporderupdate, name="outtriporderupdate"),
    path('outdel/<str:id>/', views.outdel, name='outdel'),
    path('outup/<str:id>/', views.outup, name='outup'),
    path('deltriphistory', views.deltriphistory, name='deltriphistory'),
    path('deltriporderhistory/<str:id>', views.deltriporderhistory, name="deltriporderhistory"),
    path('delbattahistory', views.delbattahistory, name='delbattahistory'),
    path('delbattaorderhistory/<str:id>', views.delbattaorderhistory, name="delbattaorderhistory"),
    path('delexpensehistory', views.delexpensehistory, name='delexpensehistory'),
    path('delexpenseorderhistory/<str:id>', views.delexpenseorderhistory, name="delexpenseorderhistory"),
    path('fullstaffview', views.fullstaffview, name="fullstaffview"),

]
