import base64
from datetime import datetime, timedelta, date
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
import cv2
from bs4 import BeautifulSoup
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template, render_to_string
from openpyxl.styles import Font
from openpyxl.workbook import Workbook
from xhtml2pdf import pisa
from .forms import *
from .models import *
from django.http import HttpResponse, HttpResponseRedirect
import num2words
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

def register(request):
    if 'username' in request.session:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'User registered successfully!')
                return render(request, 'admin/user/register.html', {'form': form})
        else:
            form = UserCreationForm()
        return render(request, 'admin/user/register.html', {'form': form})
    else:
        return redirect('login')

def staffindex(request):
    return render(request,'staffindex.html')

def login(request):
    if request.method == 'POST':
        form = logform(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['uname']
            pas = form.cleaned_data['pas']
            user = authenticate(request, username=uname, password=pas)
            if user is not None:
                auth_login(request, user)
                # Set session variables
                request.session['username'] = uname
                request.session['is_superuser'] = user.is_superuser
                if user.is_superuser:
                    return redirect('adminhome')
                else:
                    return redirect('staffhome')
            else:
                messages.error(request, 'Incorrect username or password')
        else:
            messages.error(request, 'Invalid form data')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return HttpResponseRedirect('/')

def userview(request):
    if 'username' in request.session:
        users = User.objects.filter(is_superuser=False,is_active=True)
        return render(request,'admin/user/viewuser.html',{'users':users})
    else:
        return redirect('login')

def userdel(request,username):
    if 'username' in request.session:
        user = User.objects.get(username=username)
        user.is_active = False
        user.save()
        return redirect('userview')
    else:
        return redirect('login')

def adminhome(request):
    if 'username' in request.session:
        username = request.session['username']
        # You can use the username variable here
        return render(request,'admin/adminhome.html',{'username': username})
    else:
        # If the username is not in the session, redirect to the login page
        return redirect('login')

def staffhome(request):
    if 'username' in request.session:
        username = request.session['username']
        # You can use the username variable here
        return render(request, 'staff/staffhome.html', {'username': username})
    else:
        # If the username is not in the session, redirect to the login page
        return redirect('login')

def truckreg(request):
    if 'username' in request.session:
        x = transportermodel.objects.all()
        y = drivermodel.objects.all()
        if request.method == 'POST':
            code = request.POST.get('code')
            if truckmodel.objects.filter(code=code).exists():
                messages.error(request, 'Truck with this code already exists!')
                return render(request, 'staff/register/truckreg.html', {"data": x, "data1": y})
            else:
                driverid = request.POST.get('driver')
                driver = drivermodel.objects.get(driver=driverid)
                transid = request.POST.get('trans')
                trans = transportermodel.objects.get(trans=transid)
                feet = request.POST.get('feet')
                truckmodel.objects.create(code=code, trans=trans, feet=feet, driver=driver)
                request.session['truck_registered'] = True
                return redirect('truckreg')
        else:
            if 'truck_registered' in request.session:
                messages.success(request, 'Truck registered successfully!')
                del request.session['truck_registered']
            return render(request, 'staff/register/truckreg.html', {"data": x, "data1": y})
    else:
        return redirect('login')

def driver(request):
    if 'username' in request.session:
        if request.method == 'POST':
            driver = request.POST.get('driver')
            if drivermodel.objects.filter(driver=driver).exists():
                messages.error(request, 'Driver already exists!')
                return render(request, 'staff/register/driver.html')
            else:
                drivermodel.objects.create(driver=driver)
                request.session['driver_added'] = True
                return redirect('driver')
        else:
            if 'driver_added' in request.session:
                messages.success(request, 'Driver added successfully!')
                del request.session['driver_added']
            return render(request, 'staff/register/driver.html')
    else:
        return redirect('login')

def shift(request):
    if 'username' in request.session:
        if request.method == 'POST':
            trip = request.POST.get('trip')
            if shiftmodel.objects.filter(trip=trip).exists():
                messages.error(request, 'Shift for this trip already exists!')
                return render(request, 'staff/register/shift.html')
            else:
                shiftmodel.objects.create(trip=trip)
                request.session['shift_added'] = True
                return redirect('shift')
        else:
            if 'shift_added' in request.session:
                messages.success(request, 'Shift added successfully!')
                del request.session['shift_added']
            return render(request, 'staff/register/shift.html')
    else:
        return redirect('login')

def transporterreg(request):
    if 'username' in request.session:
        if request.method == 'POST':
            t = transporterform(request.POST)
            if t.is_valid():
                trans = t.cleaned_data['trans']
                if transportermodel.objects.filter(trans=trans).exists():
                    messages.error(request, 'Transporter already exists!')
                    return render(request, 'staff/register/transporterreg.html')
                else:
                    b = transportermodel(trans=trans)
                    b.save()
                    messages.success(request, 'Transporter registered successfully!')
                    return redirect('transporterreg')
            else:
                messages.error(request, 'Invalid form data')
                return render(request, 'staff/register/transporterreg.html')
        else:
            return render(request, 'staff/register/transporterreg.html')
    else:
        return redirect('login')

def party(request):
    if 'username' in request.session:
        if request.method == 'POST':
            t = partyform(request.POST)
            if t.is_valid():
                party = t.cleaned_data['party']
                add = t.cleaned_data['add']
                if partymodel.objects.filter(party=party).exists():
                    messages.error(request, 'Party already exists!')
                    return render(request, 'staff/register/party.html')
                else:
                    b = partymodel(party=party, add=add)
                    b.save()
                    request.session['party_added'] = True
                    messages.success(request, 'Party added successfully!')
                    return redirect('party')
            else:
                return HttpResponse("not saved")
        return render(request, 'staff/register/party.html')
    else:
        return redirect('login')

def place(request):
    if 'username' in request.session:
        if request.method == 'POST':
            t = placeform(request.POST)
            if t.is_valid():
                place = t.cleaned_data['place']
                if placemodel.objects.filter(place=place).exists():
                    messages.error(request, 'Place already exists!')
                    return render(request, 'staff/register/place.html')
                else:
                    b = placemodel(place=place)
                    b.save()
                    request.session['place_added'] = True
                    return redirect('place')
            else:
                return HttpResponse("not saved")
        else:
            if 'place_added' in request.session:
                messages.success(request, 'Place added successfully!')
                del request.session['place_added']
            return render(request, 'staff/register/place.html')
    else:
        return redirect('login')

def triporder(request):
    if 'username' in request.session:
        x = placemodel.objects.all()
        y = shiftmodel.objects.all()
        z = partymodel.objects.all()
        a = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            codeid = request.POST.get('code')
            try:
                code = truckmodel.objects.get(code=codeid)
            except truckmodel.DoesNotExist:
                messages.error(request, "Truck not found")
                return redirect('triporder')
            driver = code.driver
            dat = request.POST.get('dat')
            dis = request.POST.get('dis')
            disqnt = request.POST.get('disqnt')
            partyid = request.POST.get('party')
            try:
                party = partymodel.objects.get(party=partyid)
            except partymodel.DoesNotExist:
                messages.error(request, "Party not found")
                return redirect('triporder')
            placeid = request.POST.get('place')
            try:
                place = placemodel.objects.get(place=placeid)
            except placemodel.DoesNotExist:
                messages.error(request, "Place not found")
                return redirect('triporder')
            tripid = request.POST.get('trip')
            try:
                trip = shiftmodel.objects.get(trip=tripid)
            except shiftmodel.DoesNotExist:
                messages.error(request, "Trip not found")
                return redirect('triporder')
            bno = request.POST.get('bno')
            halt=request.POST.get('halt')
            hire=request.POST.get('hire')
            cont = request.POST.get('cont')
            com = request.POST.get('com')
            created_by = request.user
            tripmodel.objects.create(code=code, driver=driver, dat=dat, party=party, place=place, trip=trip, bno=bno, dis=dis,
                                     disqnt=disqnt, created_by=created_by,halt=halt,hire=hire,cont=cont,com=com)
            request.session['trip_order_created'] = True
            return redirect('triporder')
        else:
            if 'trip_order_created' in request.session:
                messages.success(request, 'Trip order created successfully!')
                del request.session['trip_order_created']
            return render(request, 'staff/ISA/trip/triporder.html', {"d": x, "d1": y, "d2": z, "d3": a})
    else:
        return redirect('login')

def triporderupdate(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and ( code == '' or code == '----------------------------------Select---------------------------------------'):
                    return render(request, 'staff/ISA/trip/triporderupdate.html', {'code': isa_trucks})
                filter_kwargs = {}

                if code and code != '----------------------------------Select---------------------------------------':
                    filter_kwargs['code'] = code

                if frdate and todate:
                    filter_kwargs['dat__range'] = [frdate, todate]

                trips = tripmodel.objects.filter(**filter_kwargs).order_by('dat')
                if trips.exists():
                    combined_data = []
                    diesel = 0
                    hire = 0
                    halt=0
                    for trip in trips:
                        trans_data = truckmodel.objects.filter(code=trip.code, trans='ISA').first()
                        if trans_data:
                            diesel += trip.dis
                            halt += trip.halt
                            hire += trip.hire
                            combined_data.append({'trip': trip})

                    return render(request, 'staff/ISA/trip/triporderupdate.html', {'ser1': combined_data,
                                                        'diesel': diesel, 'hire': hire, 'code': isa_trucks,'halt':halt})
                else:
                    messages.error(request, 'No trips found.')
                    return render(request, 'staff/ISA/trip/triporderupdate.html', {'code': isa_trucks})
            except tripmodel.DoesNotExist:
                messages.error(request, 'No trips found.')
                return render(request, 'staff/ISA/trip/triporderupdate.html', {'code': isa_trucks})
        return render(request, 'staff/ISA/trip/triporderupdate.html', {'code': isa_trucks})
    else:
        return redirect('login')

def isaup(request, id):
    if 'username' in request.session:
        party = partymodel.objects.all()
        place = placemodel.objects.all()
        type = shiftmodel.objects.all()

        try:
            expense = tripmodel.objects.get(pk=id)
        except tripmodel.DoesNotExist:
            messages.error(request, "Expense not found.")
            return redirect('triporderupdate')
        bill=billmodel.objects.filter(bno=expense.bno)
        if request.method == 'POST':
            expense.party = partymodel.objects.get(pk=request.POST.get('party'))
            expense.place = placemodel.objects.get(pk=request.POST.get('place'))
            expense.trip = shiftmodel.objects.get(pk=request.POST.get('trip'))
            expense.hire = request.POST.get('hire')
            expense.halt = request.POST.get('halt')
            expense.dis = request.POST.get('dis')
            expense.disqnt = request.POST.get('disqnt')
            expense.updated_by = request.user
            expense.cont=request.POST.get('cont')
            expense.save()
            messages.success(request, "Expense updated successfully.")
            return redirect('triporderupdate')
        if bill.exists():
            bill.update(hire=expense.hire)
        else:
            pass
        return render(request, 'staff/ISA/trip/isaup.html', {'code': expense, 'party': party, 'place': place, 'type': type})
    else:
        return redirect('login')

@transaction.atomic
def isadel(request, id):
    trip = get_object_or_404(tripmodel, pk=id)
    try:
        batta = battamodel.objects.get(pk=trip.battaid)
        batta.deleted_by=request.user
        batta.delete()
    except battamodel.DoesNotExist:
        pass
    try:
        exp = expensemodel.objects.get(pk=trip.expid)
        exp.deleted_by=request.user
        exp.delete()
    except expensemodel.DoesNotExist:
        pass
    trip.deleted_by=request.user
    trip.delete()
    return redirect('triporderupdate')

def triphistory(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.all()
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')

                if(not frdate or frdate == '') and (not todate or todate == '') and (
                            code == '' or code == '----------------------------------Select---------------------------------------'):
                    return render(request, 'admin/history/triphistory.html', {'code': isa_trucks})

                filter_kwargs = {}

                if code and code != '----------------------------------Select---------------------------------------':
                    filter_kwargs['code'] = code

                if frdate and todate:
                    filter_kwargs['dat__range'] = [frdate, todate]

                trips = tripmodel.objects.filter(**filter_kwargs).order_by('-dat')
                deleted_trips = tripmodel.history.filter(history_type__in=['-', '~', '+'], **filter_kwargs).order_by('dat')
                if trips.exists() or deleted_trips.exists():
                    combined_data = []
                    diesel = 0
                    hire = 0
                    for trip in trips:
                        bill_data = billmodel.objects.filter(bno=trip.bno)
                        trans_data = truckmodel.objects.filter(code=trip.code).first()
                        if trans_data:
                            diesel += trip.dis
                            hire += trip.hire
                        combined_data.append({'trip': trip, 'bill': bill_data, 'trans': trans_data})

                    return render(request, 'admin/history/triphistory.html', {'ser1': combined_data, 'diesel': diesel, 'hire': hire, 'code': isa_trucks, 'deleted_trips': deleted_trips})
                else:
                    messages.error(request, 'No trips found.')
                    return render(request, 'admin/history/triphistory.html', {'code': isa_trucks})
            except tripmodel.DoesNotExist:
                messages.error(request, 'No trips found.')
                return render(request, 'admin/history/triphistory.html', {'code': isa_trucks})

        if 'trip_data' in request.session:
            combined_data = request.session['trip_data']
            diesel = request.session['diesel']
            hire = request.session['hire']
            return render(request, 'admin/history/triphistory.html', {'ser1': combined_data, 'diesel': diesel, 'hire': hire, 'code': isa_trucks})
        return render(request, 'admin/history/triphistory.html', {'code': isa_trucks})
    else:
        return redirect('login')

def triporderhistory(request, id):
    if 'username' in request.session:
        try:
            trip = tripmodel.objects.get(id=id)
            history = trip.history.all()
            history.update(created_at=timezone.localtime(trip.created_at), updated_at=timezone.localtime(trip.updated_at))
            return render(request, 'admin/history/triporderhistory.html', {'history': history})
        except tripmodel.DoesNotExist:
            messages.error(request, 'Trip not found')
            return render(request, 'admin/history/triporderhistory.html')
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'admin/history/triporderhistory.html')
    else:
        return redirect('login')

def deltriphistory(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.all()
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')

                if (not frdate or frdate == '') and (not todate or todate == '') and (code == '' or code == '----------------------------------Select---------------------------------------'):
                    return render(request, 'admin/history/deltriphistory.html', {'code': isa_trucks})

                filter_kwargs = {'history_type__in': ['-']}

                if code and code != '----------------------------------Select---------------------------------------':
                    filter_kwargs['code'] = code

                if frdate and todate:
                    filter_kwargs['dat__range'] = [frdate, todate]

                deleted_trips = tripmodel.history.filter(**filter_kwargs).order_by('-dat')
                if deleted_trips.exists():
                    return render(request, 'admin/history/deltriphistory.html', {'ser1': deleted_trips,'code': isa_trucks })
                else:
                    messages.error(request, 'No trips found.')
                    return render(request, 'admin/history/deltriphistory.html', {'code': isa_trucks})
            except tripmodel.DoesNotExist:
                messages.error(request, 'No trips found.')
                return render(request, 'admin/history/deltriphistory.html', {'code': isa_trucks})

        return render(request, 'admin/history/deltriphistory.html', {'code': isa_trucks})
    else:
        return redirect('login')

def deltriporderhistory(request,id):
    if 'username' in request.session:
        try:
            history = tripmodel.history.filter(id=id)
            return render(request, 'admin/history/deltriporderhistory.html', {'history': history})
        except tripmodel.DoesNotExist:
            messages.error(request, 'Trip not found')
            return render(request, 'admin/history/deltriporderhistory.html')
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'admin/history/deltriporderhistory.html')
    else:
        return redirect('login')

def vehicle(request):
    if 'username' not in request.session:
        return redirect('login')

    today = timezone.localdate()

    try:
        trip = tripmodel.objects.filter(code__trans='ISA').exclude(dat=today)

        if trip.exists():
            latest_trip = trip.latest('dat')
            latest_day = datetime.strptime(latest_trip.dat, '%Y-%m-%d').date()
            diff = (today - latest_day).days

            if diff >= 1:
                day = today - timezone.timedelta(days=diff)
                day = day.strftime('%Y-%m-%d')

                current_trips = tripmodel.objects.filter(dat=today).exclude(place__in=['NO WORK', 'WORKSHOP'])
                previous_trips = tripmodel.objects.filter(dat=day, place__in=['NO WORK', 'WORKSHOP']).exclude(code__in=[t.code for t in current_trips]).order_by('dat')

                return render(request, 'staff/ISA/trip/vehicle.html', {'trucks': previous_trips})
            else:
                return render(request, 'staff/ISA/trip/vehicle.html')
        else:
            return render(request, 'staff/ISA/trip/vehicle.html')

    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'staff/ISA/trip/vehicle.html')

def outtriporder(request):
    x = placemodel.objects.all()
    y = shiftmodel.objects.all()
    z = partymodel.objects.all()
    a = truckmodel.objects.exclude(trans='ISA')
    if request.method == 'POST':
        codeid = request.POST.get('code')
        try:
            code = truckmodel.objects.get(code=codeid)
        except truckmodel.DoesNotExist:
            messages.error(request, "Truck not found")
            return redirect('outtriporder')
        driver = code.driver
        dat = request.POST.get('dat')
        dis = request.POST.get('dis')
        hire = request.POST.get('hire')
        halt = request.POST.get('halt')
        disqnt = request.POST.get('disqnt')
        buy = request.POST.get('buy')
        outadv = request.POST.get('outadv')
        partyid = request.POST.get('party')
        try:
            party = partymodel.objects.get(party=partyid)
        except partymodel.DoesNotExist:
            messages.error(request, "Party not found")
            return redirect('outtriporder')

        placeid = request.POST.get('place')
        try:
            place = placemodel.objects.get(place=placeid)
        except placemodel.DoesNotExist:
            messages.error(request, "Place not found")
            return redirect('outtriporder')

        tripid = request.POST.get('trip')
        try:
            trip = shiftmodel.objects.get(trip=tripid)
        except shiftmodel.DoesNotExist:
            messages.error(request, "Trip not found")
            return redirect('outtriporder')
        created_by = request.user
        cont=request.POST.get('cont')
        bno = request.POST.get('bno')
        tripmodel.objects.create(code=code,driver=driver, dat=dat, party=party, place=place, trip=trip, dis=dis,bno=bno,
                                 disqnt=disqnt,buy=buy,created_by=created_by,hire=hire,halt=halt,cont=cont,outadv=outadv)
        return redirect('outtriporder')
    else:
        return render(request, 'staff/out/outtriporder.html', {"d": x, "d1": y, "d2": z, "d3": a})

def outtriporderupdate(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.exclude(trans='ISA')
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and ( code == '' or code == '----------------------------------Select---------------------------------------'):
                    return render(request, 'staff/out/outtriporderupdate.html', {'code': isa_trucks})
                filter_kwargs = {}

                if code and code != '----------------------------------Select---------------------------------------':
                    filter_kwargs['code'] = code

                if frdate and todate:
                    filter_kwargs['dat__range'] = [frdate, todate]

                trips = tripmodel.objects.filter(**filter_kwargs).order_by('dat')
                if trips.exists():
                    combined_data = []
                    diesel = 0
                    hire = 0
                    halt=0
                    for trip in trips:
                        trans_data = truckmodel.objects.filter(code=trip.code).exclude(trans='ISA').first()
                        if trans_data:
                            diesel += trip.dis
                            halt += trip.halt
                            hire += trip.hire
                            combined_data.append({'trip': trip})

                    return render(request, 'staff/out/outtriporderupdate.html', {'ser1': combined_data,
                                                        'diesel': diesel, 'hire': hire, 'code': isa_trucks,'halt':halt})
                else:
                    messages.error(request, 'No trips found.')
                    return render(request, 'staff/out/outtriporderupdate.html', {'code': isa_trucks})
            except tripmodel.DoesNotExist:
                messages.error(request, 'No trips found.')
                return render(request, 'staff/out/outtriporderupdate.html', {'code': isa_trucks})
        return render(request, 'staff/out/outtriporderupdate.html', {'code': isa_trucks})
    else:
        return redirect('login')

def outup(request, id):
    if 'username' in request.session:
        party = partymodel.objects.all()
        place = placemodel.objects.all()
        type = shiftmodel.objects.all()
        try:
            expense = tripmodel.objects.get(pk=id)
        except tripmodel.DoesNotExist:
            messages.error(request, "Expense not found.")
            return redirect('outtriporderupdate')
        if request.method == 'POST':
            expense.party = partymodel.objects.get(pk=request.POST.get('party'))
            expense.place = placemodel.objects.get(pk=request.POST.get('place'))
            expense.trip = shiftmodel.objects.get(pk=request.POST.get('trip'))
            expense.hire = request.POST.get('hire')
            expense.halt = request.POST.get('halt')
            expense.dis = request.POST.get('dis')
            expense.disqnt = request.POST.get('disqnt')
            expense.updated_by = request.user
            expense.cont=request.POST.get('cont')
            expense.buy = request.POST.get('buy')
            expense.outadv = request.POST.get('outadv')
            expense.save()
            messages.success(request, "Expense updated successfully.")
            return redirect('outtriporderupdate')
        else:
            pass
        return render(request, 'staff/out/outup.html', {'code': expense, 'party': party, 'place': place, 'type': type})
    else:
        return redirect('login')

@transaction.atomic
def outdel(request,id):
    trip = get_object_or_404(tripmodel, pk=id)
    trip.delete()
    return redirect('outtriporderupdate')

def handle_form_submission(request):
    """ Handles the form submission for the bill page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    if request.method == 'POST' and 'ser' in request.POST:
        start_date = request.POST.get('dat')
        end_date = request.POST.get('todate')
        party = request.POST.getlist('party')
        place = request.POST.getlist('place')

        # Check if any filters are selected
        if not party and not place and not start_date and not end_date:
            return render(request, 'staff/ISA/bill/bill.html', {'places': placemodel.objects.all(), 'parties': partymodel.objects.all()})

        # Filter trips based on the selected criteria
        filter_kwargs = {
            'bill': False,
        }
        if party:
            filter_kwargs['party__in'] = party
        if place:
            filter_kwargs['place__in'] = place
        if start_date and end_date:
            filter_kwargs['dat__range'] = [start_date, end_date]

        trips = tripmodel.objects.filter(**filter_kwargs).order_by('dat').exclude(place__in=['NO WORK', 'WORKSHOP'])

        # Render the bill page with the filtered trips
        if trips.exists():
            combined = []
            for trip in trips:
                trans_data = truckmodel.objects.filter(code=trip.code, trans='ISA')
                if trans_data:
                    combined.append({'trip': trip})
            return render(request, 'staff/ISA/bill/bill.html', {'trips': combined, 'places': placemodel.objects.all(), 'parties': partymodel.objects.all()})
        else:
            messages.error(request, 'No trips found.')
            return render(request, 'staff/ISA/bill/bill.html', {'places': placemodel.objects.all(), 'parties': partymodel.objects.all()})

def generate_bill(request):
    """
    Generates the bill for the selected trips.
    """
    if request.method == 'POST' and 'gen' in request.POST:
        id_list = request.POST.getlist('boxes')
        try:
            for trip_code in id_list:
                trips = tripmodel.objects.filter(pk=trip_code)
                trips.update(checked=True)
            return redirect('billing')
        except tripmodel.DoesNotExist:
            messages.error(request, "No trips found.")
            return redirect('bill')

def bill(request):
    """
    Renders the bill page.
    """
    if 'username' in request.session:
        parties = partymodel.objects.all()
        places = placemodel.objects.all()

        if request.method == 'POST':
            if 'ser' in request.POST:
                return handle_form_submission(request)
            elif 'gen' in request.POST:
                return generate_bill(request)
        return render(request, 'staff/ISA/bill/bill.html', {'places': places,'parties': parties})
    else:
        return redirect('login')

def billing(request):
    if 'username' in request.session:
        trip=tripmodel.objects.filter(checked=True)
        return render(request,'staff/ISA/bill/billing.html',{'trips':trip})
    else:
        return redirect('login')

def delrow(request,id):
    x=tripmodel.objects.filter(id=id)
    x.update(checked=False)
    return redirect('billing')

def billdetails(request):
    if 'username' in request.session:
        hire=0
        halt=0
        dis = 0
        haltqnt=0
        hireqnt=0
        cont=[]
        last_bill = billmodel.objects.all().order_by('bno').last()
        if last_bill:
            bno= last_bill.bno + 1
        else:
            bno= 100
        trips = tripmodel.objects.filter(checked=True)
        for trip in trips:
            halt = trip.halt
            dis += trip.dis
            if halt>0:
                haltqnt+=1
            if trip.hire>0:
                hireqnt+=1
            if trip.cont!='NIL':
                cont.append(trip.cont)
        for trip in trips:
            hire = trip.hire
            break
        bdate = timezone.localdate()
        if request.method == 'POST':
            if 'down' in request.POST:
                try:
                    bno = request.POST.get('bno')
                    diesel = request.POST.get('diesel')
                    hire = request.POST.get('hire')
                    hireqnt = request.POST.get('hireqnt')
                    toll = request.POST.get('toll')
                    tollqnt = request.POST.get('tollqnt')
                    unload = request.POST.get('unload')
                    unloadqnt = request.POST.get('unloadqnt')
                    enblock = request.POST.get('enblock')
                    enblockqnt = request.POST.get('enblockqnt')
                    shift = request.POST.get('shift')
                    shiftqnt = request.POST.get('shiftqnt')
                    weigh = request.POST.get('weigh')
                    halt = request.POST.get('halt')
                    weighqnt = request.POST.get('weighqnt')
                    haltqnt = request.POST.get('haltqnt')
                    bill = billmodel.objects.create(
                        bno=bno,bdate=bdate,diesel=diesel,hire=hire,hireqnt=hireqnt,toll=toll,tollqnt=tollqnt,unload=unload,
                        unloadqnt=unloadqnt,enblock=enblock,enblockqnt=enblockqnt,shift=shift,shiftqnt=shiftqnt,weigh=weigh,halt=halt,
                        weighqnt=weighqnt,haltqnt=haltqnt,created_by = request.user)
                    bill.save()
                    tripmodel.objects.filter(checked=True).update(bno=bno,updated_by=request.user)
                    return redirect('billpdf')

                except Exception as e:
                    messages.error(request, f"Error saving bill: {e}")
                    print(f"Error saving bill: {e}")
                    return redirect('billdetails')
        return render(request, 'staff/ISA/bill/billdetails.html',{'hireqnt': hireqnt, 'hire': hire,'halt': halt,
                                        'haltqnt':haltqnt,'dis': dis,'cont':cont,'bno':bno,'bdate':bdate})
    else:
        return redirect('login')

def billpdf(request):
    trip=tripmodel.objects.filter(checked=True)
    bils=''
    conts=[]
    code=[]
    for i in trip:
        bils=i.dat
    date_format = "%Y-%m-%d"
    bills=datetime.strptime(bils,date_format)
    for i in trip:
        if i.cont != 'NIL':
            cont_values = i.cont.split(',')  # split on comma
            conts.extend(cont_values)  # append each value to conts
            code.append(i.code)
    word_count = len(conts)
    for i in trip:
        place=i.place
        party=i.party
        feet=i.code.feet
        dat=i.dat
        date_format = "%Y-%m-%d"
        date = datetime.strptime(dat, date_format)
        add=i.party.add
        break
    bill = billmodel.objects.filter(bno=trip.first().bno)
    ttoll=tweigh=tenblock=tunload=thalt=tshift=total=thire=0
    words=''
    day=0
    for i in bill:
        bdate = datetime.strptime(i.bdate, "%Y-%m-%d")
        thire += i.hireqnt * i.hire
        ttoll += i.tollqnt * i.toll
        tweigh += i.weighqnt * i.weigh
        tenblock += i.enblockqnt * i.enblock
        tunload += i.unloadqnt * i.unload
        thalt += i.haltqnt * i.halt
        tshift += i.shiftqnt * i.shift
        total += thire + tshift + thalt + ttoll + tunload + tenblock + tweigh - i.diesel
        words += num2words.num2words(total)

        date1 = datetime.strptime(i.bdate, "%Y-%m-%d")
        date_object = datetime.strptime(dat, "%Y-%m-%d")
        day += ((date1 - date_object).days) - 1
    bill.update(total=total)
    current_year = datetime.now().year
    if datetime.now().month == 12 and datetime.now().day > 31:
        next_academic_year = f"{current_year+1}-{str(current_year + 2)[-2:]}"
    else:
        next_academic_year = f"{current_year}-{str(current_year + 1)[-2:]}"
    qr_path = 'static/img/tholadan/tholadqr.jpg'
    qr = cv2.imread(qr_path)
    resized_img = cv2.resize(qr, (150, 150))
    success, buffer = cv2.imencode('.png', resized_img)
    qr_data = buffer.tobytes()
    qr_image = base64.b64encode(qr_data).decode('utf-8')
    template = get_template('staff/ISA/bill/ex.html')

    context = {'qr': qr_image,'trip':trip,'bill':bill,'place':place,'party':party,'feet':feet,'add':add,'ttoll': ttoll,
               'thire': thire, 'words': words,'tweigh': tweigh, 'tenblock': tenblock, 'tunload': tunload,'thalt': thalt,
               'tshift': tshift,'total': total,'count': word_count,'day':day,'dat':date,'bdate':bdate,'billdate':bills,
               'conts':conts,'code':code,'next_academic_year': next_academic_year}
    html = template.render(context)

    response = HttpResponse(content_type='application/csv')
    response['Content-Disposition'] = 'filename="bill.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    else:
        tripmodel.objects.filter(checked=True).update(checked=False,bill=True,updated_by=request.user)
    return response

def viewbill(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        parties = partymodel.objects.all()
        places = placemodel.objects.all()
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')
                placeid = request.POST.get('place')
                partyid = request.POST.get('party')
                bno = request.POST.get('bno')
                filters = {}
                if frdate and todate:
                    filters['bdate__range'] = [frdate, todate]
                if bno:
                    filters['bno'] = bno
                bills = billmodel.objects.filter(**filters).order_by('bno')
                if not bills and bno:
                    messages.error(request, 'Bill not found.')
                    return render(request, 'staff/ISA/bill/viewbill.html', {
                        'code': isa_trucks,
                        'parties': parties,
                        'places': places
                    })
                combined_data = []
                total = 0
                for bill in bills:
                    total += bill.total
                    combined_data.append({'bill': bill})
                return render(request, 'staff/ISA/bill/viewbill.html', {
                    'bill': combined_data,
                    'total': total,
                    'code': isa_trucks,
                    'parties': parties,
                    'places': places
                })
            except (tripmodel.DoesNotExist, placemodel.DoesNotExist, partymodel.DoesNotExist):
                messages.error(request, 'No trips found.')
                return render(request, 'staff/ISA/bill/viewbill.html', {
                    'code': isa_trucks,
                    'parties': parties,
                    'places': places
                })
        return render(request, 'staff/ISA/bill/viewbill.html', {
            'code': isa_trucks,
            'parties': parties,
            'places': places
        })
    else:
        return redirect('login')

def billhistory(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        parties = partymodel.objects.all()
        places = placemodel.objects.all()

        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                bno = request.POST.get('bno')
                filters = {}
                if frdate and todate:
                    filters['bdate__range'] = [frdate, todate]
                if bno:
                    filters['bno'] = bno
                bills = billmodel.objects.filter(**filters).order_by('bno')
                paginator = Paginator(bills, 5)  # Show 10 bills per page
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                combined_data = []
                for bill in page_obj:
                    combined_data.append({'bill': bill})
                return render(request, 'admin/history/billhistory.html', {
                    'bill': combined_data,
                    'code': isa_trucks,
                    'parties': parties,
                    'places': places,
                    'paginator': paginator,
                    'page_obj': page_obj
                })
            except (tripmodel.DoesNotExist, placemodel.DoesNotExist, partymodel.DoesNotExist):
                messages.error(request, 'No trips found.')
                return render(request, 'admin/history/billhistory.html', {
                    'code': isa_trucks,
                    'parties': parties,
                    'places': places
                })
        return render(request, 'admin/history/billhistory.html', {
            'code': isa_trucks,
            'parties': parties,
            'places': places
        })
    else:
        return redirect('login')

def billorderhistory(request, id):
    if 'username' in request.session:
        try:
            trip = billmodel.objects.get(pk=id)
            history = trip.history.all()
            history.update(created_at=timezone.localtime(trip.created_at), updated_at=timezone.localtime(trip.updated_at))
            return render(request, 'admin/history/billorderhistory.html', {'history': history})
        except billmodel.DoesNotExist:
            request.session['error'] = 'Trip not found'
            return render(request, 'admin/history/billorderhistory.html', {'error': 'Bill not found'})
        except Exception as e:
            request.session['error'] = str(e)
            return render(request, 'admin/history/billorderhistory.html', {'error': str(e)})
    else:
        return redirect('login')

def billupdate(request,bno):
    if 'username' in request.session:
        billd = request.POST.get('hdate')
        trips = tripmodel.objects.filter(bno=bno)
        hbill=''
        bdates = timezone.localdate()
        print(bdates)
        for i in trips:
            if i.halt>0:
                hbill = i.dat
        try:
            bill = billmodel.objects.get(pk=bno)
        except billmodel.DoesNotExist:
            messages.error(request, "Bill not found.")
            return redirect('billupdate')

        if request.method == 'POST':
            if 'update' in request.POST:
                trip = tripmodel.objects.filter(bno=bno).exclude(place='SAME')
                bill.bdate = request.POST.get('bdate')
                bill.diesel = request.POST.get('diesel')
                bill.hire = request.POST.get('hire')
                trip.hire = request.POST.get('hire')
                bill.hireqnt = request.POST.get('hireqnt')
                bill.halt = request.POST.get('halt')
                bill.haltqnt = request.POST.get('haltqnt')
                bill.weigh = request.POST.get('weigh')
                bill.weighqnt = request.POST.get('weighqnt')
                bill.unload = request.POST.get('unload')
                bill.unloadqnt = request.POST.get('unloadqnt')
                bill.toll = request.POST.get('toll')
                bill.tollqnt = request.POST.get('tollqnt')
                bill.enblock = request.POST.get('enblock')
                bill.enblockqnt = request.POST.get('enblockqnt')
                bill.shift = request.POST.get('shift')
                bill.shiftqnt = request.POST.get('shiftqnt')
                bill.updated_by = request.user
                bill.save()
                trip.update(hire=bill.hire)
                return redirect('viewbill')

            if 'down' in request.POST:
                bill = billmodel.objects.filter(bno=bno)
                trip = tripmodel.objects.filter(bno=bno)
                conts = []
                code = []
                for i in trip:
                    hbill=i.dat
                    if i.cont != 'NIL':
                        cont_values = i.cont.split(',')  # split on comma
                        conts.extend(cont_values)  # append each value to conts
                        code.append(i.code)
                if billd:
                    bills = datetime.strptime(billd, "%Y-%m-%d")
                else:
                    bills = datetime.strptime(hbill, "%Y-%m-%d")
                print(bills)
                word_count = len(conts)
                for i in trip:
                    place = i.place
                    party = i.party
                    feet = i.code.feet
                    dat = i.dat
                    date_format = "%Y-%m-%d"
                    date = datetime.strptime(dat, date_format)
                    add = i.party.add
                    break
                ttoll = tweigh = tenblock = tunload = thalt = tshift = total = thire = 0
                words = ''
                day = 0
                for i in bill:
                    thire += i.hireqnt * i.hire
                    ttoll += i.tollqnt * i.toll
                    tweigh += i.weighqnt * i.weigh
                    tenblock += i.enblockqnt * i.enblock
                    tunload += i.unloadqnt * i.unload
                    thalt += i.haltqnt * i.halt
                    tshift += i.shiftqnt * i.shift
                    total += thire + tshift + thalt + ttoll + tunload + tenblock + tweigh - i.diesel
                    words += num2words.num2words(total)
                    date1 = datetime.strptime(i.bdate, "%Y-%m-%d")
                    date_object = datetime.strptime(dat, "%Y-%m-%d")
                    day += ((date1 - date_object).days) - 1
                print(conts)
                print('container:', word_count)
                qr_path = 'static/img/tholadan/tholadqr.jpg'
                qr = cv2.imread(qr_path)
                resized_img = cv2.resize(qr, (150, 150))
                success, buffer = cv2.imencode('.png', resized_img)
                qr_data = buffer.tobytes()
                qr_image = base64.b64encode(qr_data).decode('utf-8')
                template = get_template('staff/ISA/bill/ex.html')
                current_year = datetime.now().year
                bill.update(total=total)
                if datetime.now().month == 12 and datetime.now().day > 31:
                    next_academic_year = f"{current_year+1}-{str(current_year + 2)[-2:]}"
                else:
                    next_academic_year = f"{current_year}-{str(current_year + 1)[-2:]}"
                context = {'qr': qr_image, 'trip': trip, 'bill': bill, 'place': place, 'party': party, 'feet': feet,
                           'add': add, 'ttoll': ttoll,
                           'thire': thire, 'words': words, 'tweigh': tweigh, 'tenblock': tenblock, 'tunload': tunload,
                           'thalt': thalt,'bdate':bdates,
                           'tshift': tshift, 'total': total, 'count': word_count, 'day': day, 'dat': date,
                           'next_academic_year': next_academic_year,
                           'billdate': bills,
                           'conts': conts, 'code': code}
                html = template.render(context)

                response = HttpResponse(content_type='application/csv')
                response['Content-Disposition'] = 'filename="bill.pdf"'
                pisa_status = pisa.CreatePDF(html, dest=response)

                if pisa_status.err:
                    return HttpResponse('We had some errors <pre>' + html + '</pre>')
                return response
        return render(request,'staff/ISA/bill/billupdate.html',{'bill':bill,'billdate':hbill,'bdate':bdates})
    else:
        return redirect('login')

def dailyupdate(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and (code == '' or code == '----------------------------------Select---------------------------------------'):
                    return render(request, 'admin/ISA/dailyupdate.html', {'code': isa_trucks})
                filter_kwargs = {}

                if code and code != '----------------------------------Select---------------------------------------':
                    filter_kwargs['code'] = code

                if frdate and todate:
                    filter_kwargs['dat__range'] = [frdate, todate]

                trips = tripmodel.objects.filter(**filter_kwargs).order_by('dat')
                if trips.exists():
                    combined_data = []
                    diesel = 0
                    hire = 0
                    halt=0
                    for trip in trips:
                        trans_data = truckmodel.objects.filter(code=trip.code, trans='ISA').first()
                        if trans_data:
                            diesel += trip.dis
                            halt+=trip.halt
                            hire += trip.hire
                            combined_data.append({'trip':trip})

                    return render(request, 'admin/ISA/dailyupdate.html', {'trip': combined_data,'halt':halt,
                                                                          'diesel': diesel, 'hire': hire, 'code': isa_trucks})
                else:
                    messages.error(request, 'No trips found.')
                    return render(request, 'admin/ISA/dailyupdate.html', {'code': isa_trucks})
            except tripmodel.DoesNotExist:
                messages.error(request, 'No trips found.')
                return render(request, 'admin/ISA/dailyupdate.html', {'code': isa_trucks})
        if 'combined_data' in request.session:
            combined_data = request.session['combined_data']
            diesel = request.session['diesel']
            hire = request.session['hire']
            return render(request, 'admin/ISA/dailyupdate.html', {'ser1': combined_data, 'diesel': diesel, 'hire': hire, 'code': isa_trucks})
        return render(request, 'admin/ISA/dailyupdate.html', {'code': isa_trucks})
    else:
        return redirect('login')

def stafftripview(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method=='POST':
            diesel = 0
            hire = 0
            halt = 0
            frdate = request.POST.get('frdate')
            todate = request.POST.get('todate')
            code = request.POST.get('code')
            if (not frdate or frdate == '') and (not todate or todate == '') and (
                    code == '' or code == '----------------------------------Select---------------------------------------'):
                return render(request, 'staff/reports/stafftripview.html', {'code': isa_trucks})
            filter_kwargs = {}

            if code and code != '----------------------------------Select---------------------------------------':
                filter_kwargs['code'] = code

            if frdate and todate:
                filter_kwargs['dat__range'] = [frdate, todate]

            trips = tripmodel.objects.filter(**filter_kwargs).order_by('dat')

            if 'ser1' in request.POST:
                if trips.exists():
                    combined=[]
                    for trip in trips:
                        trans_data = truckmodel.objects.filter(code=trip.code, trans='ISA').first()
                        if trans_data:
                            diesel += trip.dis
                            halt += trip.halt
                            hire += trip.hire
                            combined.append({'trip':trip})
                    return render(request, 'staff/reports/stafftripview.html', {'trip': combined, 'halt': halt,
                                                                                'diesel': diesel, 'hire': hire,
                                                                                'code': isa_trucks})

            if 'export' in request.POST:
                if trips.exists():
                    combined = []
                    for trip in trips:
                        trans_data = truckmodel.objects.filter(code=trip.code, trans='ISA').first()
                        if trans_data:
                            diesel += trip.dis
                            halt += trip.halt
                            hire += trip.hire
                            combined.append({'trip': trip})
                        total=hire+halt
                html = render_to_string('staff/reports/tripreport.html',
                                        {'trip': combined, 'diesel': diesel, 'hire': hire,'total':total,'halt':halt})
                wb = Workbook()
                ws = wb.active
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table')
                rows = table.find_all('tr')
                # Download the image

                row_idx = 1  # Initialize row index

                for row in rows:
                    cells = row.find_all('td')
                    for i, cell in enumerate(cells):
                        value = cell.text
                        if value.replace('.', '', 1).replace('-', '', 1).isdigit():  # Check if value is a number
                            ws.cell(row=row_idx, column=i + 1).value = float(value)
                            if float(value) < 0:
                                ws.cell(row=row_idx, column=i + 1).value = float(value)
                                ws.cell(row=row_idx, column=i + 1).number_format = '#,##0.00;[Red]-#,##0.00'
                            else:
                                ws.cell(row=row_idx, column=i + 1).value = float(value)
                                ws.cell(row=row_idx, column=i + 1).number_format = '#,##0.00'
                        else:
                            ws.cell(row=row_idx, column=i + 1).value = value
                        if row_idx == 1:  # Assuming the heading is in the first row
                            ws.cell(row=row_idx, column=i + 1).font = Font(bold=True)
                    row_idx += 1  # Increment row index

                # Save Excel workbook to a file
                wb.save('tripreport.xlsx')

                # Return Excel file as a response
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'filename="tripreport.xlsx"'
                wb.save(response)
                return response
        return render(request, 'staff/reports/stafftripview.html', {'code': isa_trucks})
    else:
        return redirect('login')

def outdailyupdate(request):
    if 'username' in request.session:
        x = truckmodel.objects.exclude(trans='ISA')
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and (code == '' or code == '----------------------------------Select---------------------------------------'):
                    return render(request, 'admin/out/outdailyupdate.html', {'code': x})
                if code == '' or code == '----------------------------------Select---------------------------------------':
                    if frdate and todate:
                        trips = tripmodel.objects.filter(dat__range=[frdate, todate]).order_by('dat')
                    else:
                        trips = tripmodel.objects.all().order_by('dat')
                else:
                    if frdate and todate and code:
                        trips = tripmodel.objects.filter(code=code, dat__range=[frdate, todate]).order_by('dat')
                    elif code:
                        trips = tripmodel.objects.filter(code=code).order_by('dat')
                if trips.exists():
                    combined_data = []
                    diesel = 0
                    hire = 0
                    halt = 0
                    for trip in trips:
                        trans_data = truckmodel.objects.filter(code=trip.code).exclude(trans='ISA').first()
                        if trans_data:
                            diesel += trip.dis
                            hire += trip.hire
                            halt += trip.halt
                            combined_data.append({'trip': trip,'trans': trans_data})

                    return render(request, 'admin/out/outdailyupdate.html', {'code': x, 'ser1': combined_data, 'diesel': diesel, 'hire': hire,'halt' :halt})
                else:
                    messages.error(request, 'Trip not found.')
            except tripmodel.DoesNotExist:
                messages.error(request, 'Trip not found.')
        if 'combined_data' in request.session:
            combined_data = request.session['combined_data']
            diesel = request.session['diesel']
            hire = request.session['hire']
            return render(request, 'admin/out/outdailyupdate.html', {'code': x, 'ser1': combined_data, 'diesel': diesel, 'hire': hire})
        return render(request, 'admin/out/outdailyupdate.html', {'code': x})
    else:
        return redirect('login')

def adminvehicle(request):
    if 'username' not in request.session:
        return redirect('login')

    today = timezone.localdate()

    try:
        trip = tripmodel.objects.filter(code__trans='ISA').exclude(dat=today)

        if trip.exists():
            latest_trip = trip.latest('dat')
            latest_day = datetime.strptime(latest_trip.dat, '%Y-%m-%d').date()
            diff = (today - latest_day).days

            if diff >= 1:
                day = today - timezone.timedelta(days=diff)
                day = day.strftime('%Y-%m-%d')

                current_trips = tripmodel.objects.filter(dat=today).exclude(place__in=['NO WORK', 'WORKSHOP'])
                previous_trips = tripmodel.objects.filter(dat=day, place__in=['NO WORK', 'WORKSHOP']).exclude(
                    code__in=[t.code for t in current_trips]).order_by('dat')

                return render(request, 'admin/ISA/adminvehicle.html', {'trucks': previous_trips})
            else:
                return render(request, 'admin/ISA/adminvehicle.html')
        else:
            return render(request, 'admin/ISA/adminvehicle.html')

    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'admin/ISA/adminvehicle.html')

def batta(request,id):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        isa_driver = drivermodel.objects.exclude(driver='OTHER')
        trip=tripmodel.objects.get(pk=id)
        if request.method == 'POST':
            codeid = request.POST.get('code')
            try:
                code = truckmodel.objects.get(code=codeid)
            except truckmodel.DoesNotExist:
                messages.error(request, "Truck not found")
                return redirect('batta')
            driverid = request.POST.get('driver')
            try:
                driver = drivermodel.objects.get(driver=driverid)
            except drivermodel.DoesNotExist:
                messages.error(request, "Driver not found")
                return redirect('batta')
            date = request.POST.get('date')
            sheetno = request.POST.get('sheetno')
            opkm = request.POST.get('opkm')
            clkm = request.POST.get('clkm')
            battas = request.POST.get('batta')
            lift = request.POST.get('lift')
            print = request.POST.get('print')
            othexp = request.POST.get('othexp')
            wei = request.POST.get('wei')
            halt = request.POST.get('halt')
            park = request.POST.get('park')
            rto = request.POST.get('rto')
            adv = request.POST.get('adv')
            loan = request.POST.get('loan')
            cont=request.POST.get('cont')

            total = int(battas) + int(lift) + int(print) + int(othexp) + int(wei) + int(halt) + int(
                park) + int(rto) - int(adv) - int(loan)
            created_by = request.user

            batta = battamodel.objects.create(total=total, code=code, driver=driver, date=date,sheetno=sheetno, batta=battas,
                                              lift=lift, print=print, othexp=othexp, wei=wei, halt=halt,park=park, rto=rto, adv=adv,
                                              loan=loan, created_by=created_by)
            batta.save()
            if trip:
                trip.amount = int(battas) + int(lift) + int(print) + int(othexp) + int(wei) + int(halt) + int(
                    park) + int(rto) + int(adv) + int(loan)
                trip.batta = True
                trip.sheetno = sheetno
                trip.opkm = opkm
                trip.clkm=clkm
                trip.driver = driver
                trip.battaid=batta.pk
                trip.cont=cont
                trip.updated_by = request.user
                trip.save()
            return render(request, 'staff/ISA/batta/batta.html', {'code': isa_trucks, 'driver': isa_driver,
                                                                  'trip': trip})
        return render(request, 'staff/ISA/batta/batta.html', {'code': isa_trucks, 'driver': isa_driver,
                                                              'trip':trip})
    else:
        return redirect('login')

def battaupdate(request):
    if 'username' in request.session:
        isa_driver = drivermodel.objects.exclude(driver='OTHER')
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            if 'ser1' in request.POST:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                driver = request.POST.get('driver')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and (
                        driver == '--------------------Select-------------------') and (
                        code == '--------------------Select-------------------'):
                    return render(request, 'staff/ISA/batta/battaupdate.html',
                                    {'driver': isa_driver, 'code': isa_trucks})
                # Rest of your code...
                if code != '--------------------Select-------------------' and driver != '--------------------Select-------------------':
                    if frdate and todate:
                        batta = battamodel.objects.filter(code=code, driver=driver,
                                                                 date__range=[frdate, todate]).order_by(
                            'date')
                    else:
                        batta = battamodel.objects.filter(code=code, driver=driver).order_by('date')
                elif code != '--------------------Select-------------------':
                    if frdate and todate:
                        batta = battamodel.objects.filter(code=code, date__range=[frdate, todate]).order_by(
                            'date')
                    else:
                        batta = battamodel.objects.filter(code=code).order_by('date')
                elif driver != '--------------------Select-------------------':
                    if frdate and todate:
                        batta = battamodel.objects.filter(driver=driver, date__range=[frdate, todate]).order_by(
                            'date')
                    else:
                        batta = battamodel.objects.filter(driver=driver).order_by('date')
                else:
                    if frdate and todate:
                        batta = battamodel.objects.filter(date__range=[frdate, todate]).order_by('date')
                    else:
                        batta = battamodel.objects.all().order_by('date')
                if batta:
                    totals = {
                        'batta': str(sum(e.batta for e in batta)),
                        'lift': str(sum(e.lift for e in batta)),
                        'print': str(sum(e.print for e in batta)),
                        'othexp': str(sum(e.othexp for e in batta)),
                        'wei': str(sum(e.wei for e in batta)),
                        'halt': str(sum(e.halt for e in batta)),
                        'park': str(sum(e.park for e in batta)),
                        'rto': str(sum(e.rto for e in batta)),
                        'adv': str(sum(e.adv for e in batta)),
                        'loan': str(sum(e.loan for e in batta)),
                        'total': str(sum(e.total for e in batta)),
                    }
                    return render(request, 'staff/ISA/batta/battaupdate.html',
                                    {'total': totals, 'ser1': batta, 'driver': isa_driver, 'code': isa_trucks})
                else:
                    totals = {}
                    request.session['totals'] = totals
                    messages.error(request, "Batta not found.")
                    return render(request, 'staff/ISA/batta/battaupdate.html',
                                    {'total': totals, 'driver': isa_driver, 'code': isa_trucks})
        return render(request, 'staff/ISA/batta/battaupdate.html',
                        {'driver': isa_driver, 'code': isa_trucks})
    else:
        return redirect('login')

def battaup(request,id):
    isa_driver = drivermodel.objects.exclude(driver='OTHER')
    if 'username' in request.session:
        try:
            batta = battamodel.objects.get(pk=id)
        except battamodel.DoesNotExist:
            messages.error(request, "Batta not found.")
            return redirect('battaupdate')
        trip=tripmodel.objects.get(battaid=id)
        if request.method == 'POST':
            batta.batta = request.POST.get('batta')
            batta.lift = request.POST.get('lift')
            batta.driver=drivermodel.objects.get(driver=request.POST.get('driver'))
            trip.opkm=request.POST.get('opkm')
            trip.clkm=request.POST.get('clkm')
            batta.print = request.POST.get('print')
            batta.wei = request.POST.get('wei')
            batta.halt = request.POST.get('halt')
            batta.park = request.POST.get('park')
            batta.rto = request.POST.get('rto')
            batta.adv = request.POST.get('adv')
            batta.loan = request.POST.get('loan')
            batta.othexp = request.POST.get('othexp')
            batta.updated_by = request.user
            trip.updated_by=request.user
            # Validate total calculation
            total_fields = [
                batta.batta,
                batta.lift,
                batta.print,
                batta.othexp,
                batta.wei,
                batta.halt,
                batta.park,
                batta.rto,
            ]
            trip.amount = int(batta.batta) + int(batta.lift) + int(batta.print) + int(batta.othexp) + int(batta.wei) + int(batta.halt) + int(
                batta.park) + int(batta.rto) + int(batta.adv) + int(batta.loan)
            trip.driver=drivermodel.objects.get(driver=request.POST.get('driver'))
            try:
                batta.total = (sum(map(int, total_fields)))-int(batta.adv)-int(batta.loan)
            except ValueError:
                messages.error(request, "Invalid input for total calculation.")
                return render(request, 'staff/ISA/batta/battaup.html', {'code': batta,'trip':trip})
            batta.save()
            trip.save()
            messages.success(request, "Batta updated successfully.")
            return redirect('battaupdate')
        return render(request, 'staff/ISA/batta/battaup.html', {'code': batta,'trip':trip,'driver':isa_driver})
    else:
        return redirect('login')

def battadel(request, id):
    batta = get_object_or_404(battamodel, pk=id)
    batta.deleted_by=request.user
    batta.delete()
    try:
        trip = tripmodel.objects.get(battaid=id)
        trip.battaid = 0
        trip.sheetno = 0
        trip.opkm = 0
        trip.clkm = 0
        trip.amount = 0
        trip.updated_by=request.user
        trip.save()
    except tripmodel.DoesNotExist:
        pass
    return redirect('battaupdate')

def battaview(request):
    if 'username' in request.session:
        isa_driver = drivermodel.objects.exclude(driver='OTHER')
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            if 'ser1' in request.POST:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                driver = request.POST.get('driver')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and (
                        driver == '--------------------Select-------------------') and (
                        code == '--------------------Select-------------------'):
                    return render(request, 'admin/ISA/battaview.html',
                                    {'driver': isa_driver, 'code': isa_trucks})
                # Rest of your code...
                filter_kwargs = {}

                if code != '--------------------Select-------------------':
                    filter_kwargs['code'] = code

                if driver != '--------------------Select-------------------':
                    filter_kwargs['driver'] = driver

                if frdate and todate:
                    filter_kwargs['date__range'] = [frdate, todate]

                batta = battamodel.objects.filter(**filter_kwargs).order_by('date')
                if batta:
                    totals = {
                        'batta': str(sum(e.batta for e in batta)),
                        'lift': str(sum(e.lift for e in batta)),
                        'print': str(sum(e.print for e in batta)),
                        'othexp': str(sum(e.othexp for e in batta)),
                        'wei': str(sum(e.wei for e in batta)),
                        'halt': str(sum(e.halt for e in batta)),
                        'park': str(sum(e.park for e in batta)),
                        'rto': str(sum(e.rto for e in batta)),
                        'adv': str(sum(e.adv for e in batta)),
                        'loan': str(sum(e.loan for e in batta)),
                        'total': str(sum(e.total for e in batta)),
                    }
                else:
                    totals = {}
                    messages.error(request, 'Batta not found.')
                return render(request, 'admin/ISA/battaview.html',
                                {'total': totals, 'ser1': batta, 'driver': isa_driver, 'code': isa_trucks})
        return render(request, 'admin/ISA/battaview.html',
                        {'driver': isa_driver, 'code': isa_trucks})
    else:
        return redirect('login')

def staffbattaview(request):
    if 'username' in request.session:
        isa_driver = drivermodel.objects.exclude(driver='OTHER')
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            frdate = request.POST.get('frdate')
            todate = request.POST.get('todate')
            driver = request.POST.get('driver')
            code = request.POST.get('code')
            if (not frdate or frdate == '') and (not todate or todate == '') and (
                    driver == '--------------------Select-------------------') and (
                    code == '--------------------Select-------------------'):
                return render(request, 'staff/reports/staffbattaview.html',
                              {'driver': isa_driver, 'code': isa_trucks})
            # Rest of your code...
            filter_kwargs = {}

            if code != '--------------------Select-------------------':
                filter_kwargs['code'] = code

            if driver != '--------------------Select-------------------':
                filter_kwargs['driver'] = driver

            if frdate and todate:
                filter_kwargs['date__range'] = [frdate, todate]

            batta = battamodel.objects.filter(**filter_kwargs).order_by('date')
            if batta:
                totals = {
                    'batta': str(sum(e.batta for e in batta)),
                    'lift': str(sum(e.lift for e in batta)),
                    'print': str(sum(e.print for e in batta)),
                    'othexp': str(sum(e.othexp for e in batta)),
                    'wei': str(sum(e.wei for e in batta)),
                    'halt': str(sum(e.halt for e in batta)),
                    'park': str(sum(e.park for e in batta)),
                    'rto': str(sum(e.rto for e in batta)),
                    'adv': str(sum(e.adv for e in batta)),
                    'loan': str(sum(e.loan for e in batta)),
                    'total': str(sum(e.total for e in batta)),
                }
            else:
                totals = {}
            if 'export' in request.POST:
                html = render_to_string('staff/reports/battareport.html', {'total': totals, 'ser1': batta})
                wb = Workbook()
                ws = wb.active
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table')
                rows = table.find_all('tr')
                # Download the image

                row_idx = 1  # Initialize row index

                for row in rows:
                    cells = row.find_all('td')
                    for i, cell in enumerate(cells):
                        value = cell.text
                        if value.replace('.', '', 1).replace('-', '', 1).isdigit():  # Check if value is a number
                            ws.cell(row=row_idx, column=i + 1).value = float(value)
                            if float(value) < 0:
                                ws.cell(row=row_idx, column=i + 1).value = float(value)
                                ws.cell(row=row_idx, column=i + 1).number_format = '#,##0.00;[Red]-#,##0.00'
                            else:
                                ws.cell(row=row_idx, column=i + 1).value = float(value)
                                ws.cell(row=row_idx, column=i + 1).number_format = '#,##0.00'
                        else:
                            ws.cell(row=row_idx, column=i + 1).value = value
                        if row_idx == 1:  # Assuming the heading is in the first row
                            ws.cell(row=row_idx, column=i + 1).font = Font(bold=True)
                    row_idx += 1  # Increment row index

                # Save Excel workbook to a file
                wb.save('battareport.xlsx')

                # Return Excel file as a response
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'filename="battareport.xlsx"'
                wb.save(response)
                return response

            if 'ser1' in request.POST:
                return render(request, 'staff/reports/staffbattaview.html',
                                {'total': totals, 'ser1': batta, 'driver': isa_driver, 'code': isa_trucks})

        return render(request, 'staff/reports/staffbattaview.html',{'driver': isa_driver, 'code': isa_trucks})
    else:
        return redirect('login')

def battahistory(request):
    if 'username' in request.session:
        isa_driver = drivermodel.objects.exclude(driver='OTHER')
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            if 'ser1' in request.POST:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                driver = request.POST.get('driver')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and (
                        driver == '--------------------Select-------------------') and (
                        code == '--------------------Select-------------------'):
                    return render(request, 'admin/history/battahistory.html',
                                    {'driver': isa_driver, 'code': isa_trucks})
                # Rest of your code...
                filter_kwargs = {}

                if code != '--------------------Select-------------------':
                    filter_kwargs['code'] = code

                if driver != '--------------------Select-------------------':
                    filter_kwargs['driver'] = driver

                if frdate and todate:
                    filter_kwargs['date__range'] = [frdate, todate]

                batta = battamodel.objects.filter(**filter_kwargs).order_by('date')
                if batta:
                    totals = {
                        'batta': str(sum(e.batta for e in batta)),
                        'lift': str(sum(e.lift for e in batta)),
                        'print': str(sum(e.print for e in batta)),
                        'othexp': str(sum(e.othexp for e in batta)),
                        'wei': str(sum(e.wei for e in batta)),
                        'halt': str(sum(e.halt for e in batta)),
                        'park': str(sum(e.park for e in batta)),
                        'rto': str(sum(e.rto for e in batta)),
                        'adv': str(sum(e.adv for e in batta)),
                        'loan': str(sum(e.loan for e in batta)),
                        'total': str(sum(e.total for e in batta)),
                    }
                else:
                    totals = {}
                return render(request, 'admin/history/battahistory.html',
                                {'total': totals, 'ser1': batta, 'driver': isa_driver, 'code': isa_trucks})
        return render(request, 'admin/history/battahistory.html',
                        {'driver': isa_driver, 'code': isa_trucks})
    else:
        return redirect('login')

def battaorderhistory(request, id):
    if 'username' in request.session:
        try:
            trip = battamodel.objects.get(pk=id)
            history = trip.history.all()
            history.update(created_at=timezone.localtime(trip.created_at), updated_at=timezone.localtime(trip.updated_at))
            return render(request, 'admin/history/battaorderhistory.html', {'history': history})
        except battamodel.DoesNotExist:
            request.session['error'] = 'Trip not found'
            return render(request, 'admin/history/battaorderhistory.html', {'error': 'Trip not found'})
        except Exception as e:
            request.session['error'] = str(e)
            return render(request, 'admin/history/battaorderhistory.html', {'error': str(e)})
    else:
        return redirect('login')

def delbattahistory(request):
    if 'username' in request.session:
        isa_driver = drivermodel.objects.exclude(driver='OTHER')
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            if 'ser1' in request.POST:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                driver = request.POST.get('driver')
                code = request.POST.get('code')

                if not (
                        frdate or todate or driver != '--------------------Select-------------------' or code != '--------------------Select-------------------'):
                    return render(request, 'admin/history/delbattahistory.html',
                                  {'driver': isa_driver, 'code': isa_trucks})
                filters = {}

                if code != '--------------------Select-------------------':
                    filters['code'] = code

                if driver != '--------------------Select-------------------':
                    filters['driver'] = driver

                if frdate and todate:
                    filters['date__range'] = [frdate, todate]

                batta = battamodel.history.filter(**filters,history_type__in=['-']).order_by('date')
                return render(request, 'admin/history/delbattahistory.html',
                                {'ser1': batta, 'driver': isa_driver, 'code': isa_trucks})
        return render(request, 'admin/history/delbattahistory.html',
                        {'driver': isa_driver, 'code': isa_trucks})
    else:
        return redirect('login')

def delbattaorderhistory(request, id):
    if 'username' in request.session:
        try:
            history = battamodel.history.filter(id=id)
            return render(request, 'admin/history/delbattaorderhistory.html', {'history': history})
        except battamodel.DoesNotExist:
            request.session['error'] = 'Trip not found'
            return render(request, 'admin/history/delbattaorderhistory.html', {'error': 'Trip not found'})
        except Exception as e:
            request.session['error'] = str(e)
            return render(request, 'admin/history/delbattaorderhistory.html', {'error': str(e)})
    else:
        return redirect('login')

def expense(request,id):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        trip=tripmodel.objects.get(pk=id)
        if request.method == 'POST':
            codeid = request.POST.get('code')
            try:
                code = truckmodel.objects.get(code=codeid)
            except truckmodel.DoesNotExist:
                messages.error(request, "Truck not found")
                return redirect('expense')
            date = request.POST.get('date')
            roro = request.POST.get('roro')
            adblue = request.POST.get('adblue')
            oil = request.POST.get('oil')
            insur = request.POST.get('insur')
            tax = request.POST.get('tax')
            emi = request.POST.get('emi')
            test = request.POST.get('test')
            work = request.POST.get('work')
            spare = request.POST.get('spare')
            workshop = request.POST.get('workshop')
            rethread = request.POST.get('rethread')
            tyre = request.POST.get('tyre')
            toll = request.POST.get('toll')
            park = request.POST.get('park')
            try:
                total = int(roro) + int(adblue) + int(oil) + int(insur) + int(tax) + int(emi) + int(
                    test) + int(work) + int(spare) + int(rethread) + int(tyre) + int(toll) + int(park)
            except ValueError:
                messages.error(request, "Invalid input for total calculation")
                return render(request, 'staff/ISA/expense/expense.html', {'code': isa_trucks})
            created_by = request.user
            expense=expensemodel.objects.create(code=code, date=date, roro=roro, adblue=adblue, oil=oil, insur=insur,
                                              tax=tax, emi=emi, test=test, work=work, spare=spare, workshop=workshop,
                                              rethread=rethread, tyre=tyre, toll=toll, park=park, total=total,
                                              created_by=created_by)
            messages.success(request, "Expense added successfully")
            expense.save()
            if trip:
                trip.exptotal = int(roro) + int(adblue) + int(oil) + int(insur) + int(tax) + int(emi) + int(
                    test) + int(work) + int(spare) + int(rethread) + int(tyre) + int(toll) + int(park)
                trip.expid=expense.id
                trip.updated_by = request.user
                trip.save()
            return render(request, 'staff/ISA/expense/expense.html', {'code': isa_trucks,'trip':trip})
        return render(request, 'staff/ISA/expense/expense.html', {'code': isa_trucks,'trip':trip})
    else:
        return redirect('login')

def expenseupdate(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            frdate = request.POST.get('frdate')
            todate = request.POST.get('todate')
            code = request.POST.get('code')
            if 'ser1' in request.POST:
                if (not frdate or frdate == '') and (not todate or todate == '') and (
                        code == '--------------------Select-------------------'):
                    return render(request, 'staff/ISA/expense/expenseupdate.html',
                                    {'code': isa_trucks})
                if code != '--------------------Select-------------------':
                    if frdate and todate and code:
                        expenses = expensemodel.objects.filter(code=code, date__range=[frdate, todate]).order_by('date')
                    elif code:
                        expenses = expensemodel.objects.filter(code=code).order_by('date')
                    else:
                        if frdate and todate:
                            expenses = expensemodel.objects.filter(date__range=[frdate, todate]).order_by('date')
                else:
                    if frdate and todate:
                        expenses = expensemodel.objects.filter(date__range=[frdate, todate]).order_by('date')
                if expenses:
                    totals = {
                        'roro': sum(e.roro for e in expenses),
                        'adblue': sum(e.adblue for e in expenses),
                        'oil': sum(e.oil for e in expenses),
                        'park': sum(e.park for e in expenses),
                        'insur': sum(e.insur for e in expenses),
                        'tax': sum(e.tax for e in expenses),
                        'emi': sum(e.emi for e in expenses),
                        'test': sum(e.test for e in expenses),
                        'work': sum(e.work for e in expenses),
                        'spare': sum(e.spare for e in expenses),
                        'rethread': sum(e.rethread for e in expenses),
                        'tyre': sum(e.tyre for e in expenses),
                        'toll': sum(e.toll for e in expenses),
                        'total': sum(e.total for e in expenses),
                    }
                else:
                    totals = {}
                return render(request, 'staff/ISA/expense/expenseupdate.html',
                                {'code': isa_trucks, 'ser1': expenses, 'total': totals})
        return render(request, 'staff/ISA/expense/expenseupdate.html', {'code': isa_trucks})
    else:
        return redirect('login')

def expup(request, id):
    if 'username' in request.session:
        try:
            expense = expensemodel.objects.get(pk=id)
        except expensemodel.DoesNotExist:
            messages.error(request, "Expense not found.")
            return redirect('expenseupdate')
        trip = tripmodel.objects.get(expid=id)
        if request.method == 'POST':
            expense.roro = request.POST.get('roro')
            expense.adblue = request.POST.get('adblue')
            expense.oil = request.POST.get('oil')
            expense.insur = request.POST.get('insur')
            expense.tax = request.POST.get('tax')
            expense.emi = request.POST.get('emi')
            expense.test = request.POST.get('test')
            expense.work = request.POST.get('work')
            expense.spare = request.POST.get('spare')
            expense.rethread = request.POST.get('rethread')
            expense.tyre = request.POST.get('tyre')
            expense.toll = request.POST.get('toll')
            expense.park = request.POST.get('park')
            expense.updated_by = request.user
            # Validate total calculation
            total_fields = [
                expense.roro,
                expense.adblue,
                expense.oil,
                expense.insur,
                expense.tax,
                expense.emi,
                expense.test,
                expense.work,
                expense.spare,
                expense.rethread,
                expense.tyre,
                expense.toll,
                expense.park
            ]
            try:
                expense.total = sum(map(int, total_fields))
            except ValueError:
                messages.error(request, "Invalid input for total calculation.")
                return render(request, 'staff/ISA/expense/expup.html', {'code': expense})
            trip.exptotal=sum(map(int, total_fields))
            trip.updated_by = request.user
            expense.save()
            trip.save()
            messages.success(request, "Expense updated successfully.")

            return redirect('expenseupdate')
        return render(request, 'staff/ISA/expense/expup.html', {'code': expense})
    else:
        return redirect('login')

def expdel(request, id):
    expense = get_object_or_404(expensemodel, pk=id)
    expense.deleted_by=request.user
    expense.delete()

    try:
        trip = tripmodel.objects.get(expid=id)
        trip.expid = 0
        trip.exptotal = 0
        trip.updated_by=request.user
        trip.save()
    except tripmodel.DoesNotExist:
        pass

    return redirect('expenseupdate')

def expenseview(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            if 'ser1' in request.POST:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')

                if (not frdate or frdate == '') and (not todate or todate == '') and (
                    code == '--------------------Select-------------------'):
                    return render(request, 'admin/ISA/expenseview.html', {'code': isa_trucks})

                filter_kwargs = {}

                if code != '--------------------Select-------------------':
                    filter_kwargs['code'] = code

                if frdate and todate:
                    filter_kwargs['date__range'] = [frdate, todate]

                expense = expensemodel.objects.filter(**filter_kwargs).order_by('date')
                if expense:
                    totals = {
                    'roro': sum(e.roro for e in expense),
                    'adblue': sum(e.adblue for e in expense),
                    'oil': sum(e.oil for e in expense),
                    'park': sum(e.park for e in expense),
                    'insur': sum(e.insur for e in expense),
                    'tax': sum(e.tax for e in expense),
                    'emi': sum(e.emi for e in expense),
                    'test': sum(e.test for e in expense),
                    'work': sum(e.work for e in expense),
                    'spare': sum(e.spare for e in expense),
                    'rethread': sum(e.rethread for e in expense),
                    'tyre': sum(e.tyre for e in expense),
                    'toll': sum(e.toll for e in expense),
                    'total': sum(e.total for e in expense),
                    }
                else:
                    totals = {}
                    messages.error(request, 'Expense not found.')
                return render(request, 'admin/ISA/expenseview.html',
                          {'expenses': expense, 'code': isa_trucks, 'total': totals})
        return render(request, 'admin/ISA/expenseview.html', {'code': isa_trucks})
    else:
        return redirect('login')

def staffexpview(request):
    isa_trucks = truckmodel.objects.filter(trans='ISA')

    if request.method == 'POST':
        frdate = request.POST.get('frdate')
        todate = request.POST.get('todate')
        code = request.POST.get('code')
        if (not frdate or frdate == '') and (not todate or todate == '') and (
                code == '--------------------Select-------------------'):
            return render(request, 'staff/reports/staffexpview.html', {'code': isa_trucks})

        filter_kwargs = {}

        if code != '--------------------Select-------------------':
            filter_kwargs['code'] = code

        if frdate and todate:
            filter_kwargs['date__range'] = [frdate, todate]

        expenses = expensemodel.objects.filter(**filter_kwargs).order_by('date')

        if expenses:
            totals = {
                'roro': sum(e.roro for e in expenses),
                'adblue': sum(e.adblue for e in expenses),
                'oil': sum(e.oil for e in expenses),
                'park': sum(e.park for e in expenses),
                'insur': sum(e.insur for e in expenses),
                'tax': sum(e.tax for e in expenses),
                'emi': sum(e.emi for e in expenses),
                'test': sum(e.test for e in expenses),
                'work': sum(e.work for e in expenses),
                'spare': sum(e.spare for e in expenses),
                'rethread': sum(e.rethread for e in expenses),
                'tyre': sum(e.tyre for e in expenses),
                'toll': sum(e.toll for e in expenses),
                'total': sum(e.total for e in expenses),
            }
        else:
            totals = {}
        if 'export' in request.POST:
            html = render_to_string('staff/reports/expreport.html', {'total': totals, 'ser1': expenses})
            wb = Workbook()
            ws = wb.active
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table')
            rows = table.find_all('tr')
            row_idx = 1  # Initialize row index

            for row in rows:
                cells = row.find_all('td')
                for i, cell in enumerate(cells):
                    value = cell.text
                    if value.replace('.', '', 1).replace('-', '', 1).isdigit():  # Check if value is a number
                        ws.cell(row=row_idx, column=i + 1).value = float(value)
                        if float(value) < 0:
                            ws.cell(row=row_idx, column=i + 1).value = float(value)
                            ws.cell(row=row_idx, column=i + 1).number_format = '#,##0.00;[Red]-#,##0.00'
                        else:
                            ws.cell(row=row_idx, column=i + 1).value = float(value)
                            ws.cell(row=row_idx, column=i + 1).number_format = '#,##0.00'
                    else:
                        ws.cell(row=row_idx, column=i + 1).value = value
                    if row_idx == 1:  # Assuming the heading is in the first row
                        ws.cell(row=row_idx, column=i + 1).font = Font(bold=True)
                row_idx += 1  # Increment row index

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="expensereport.xlsx"'
            wb.save(response)
            return response

        if 'ser1':
            return render(request, 'staff/reports/staffexpview.html',
                          {'ser1': expenses, 'code': isa_trucks, 'total': totals})

    return render(request, 'staff/reports/staffexpview.html', {'code': isa_trucks})

def expensehistory(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            if 'ser1' in request.POST:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and (code == '--------------------Select-------------------'):
                    return render(request, 'admin/history/expensehistory.html', {'code': isa_trucks})
                filter_kwargs = {}

                if code != '--------------------Select-------------------':
                    filter_kwargs['code'] = code

                if frdate and todate:
                    filter_kwargs['date__range'] = [frdate, todate]

                expense = expensemodel.objects.filter(**filter_kwargs).order_by('date')
                if expense:
                    totals = {
                    'roro': sum(e.roro for e in expense),
                    'adblue': sum(e.adblue for e in expense),
                    'oil': sum(e.oil for e in expense),
                    'park': sum(e.park for e in expense),
                    'insur': sum(e.insur for e in expense),
                    'tax': sum(e.tax for e in expense),
                    'emi': sum(e.emi for e in expense),
                    'test': sum(e.test for e in expense),
                    'work': sum(e.work for e in expense),
                    'spare': sum(e.spare for e in expense),
                    'rethread': sum(e.rethread for e in expense),
                    'tyre': sum(e.tyre for e in expense),
                    'toll': sum(e.toll for e in expense),
                    'total': sum(e.total for e in expense),
                    }
                else:
                    totals = {}
                return render(request, 'admin/history/expensehistory.html',
                                {'expenses': expense, 'code': isa_trucks, 'total': totals})
        return render(request, 'admin/history/expensehistory.html', {'code': isa_trucks})
    else:
        return redirect('login')

def expenseorderhistory(request, id):
    if 'username' in request.session:
        try:
            trip = expensemodel.objects.get(id=id)
            history = trip.history.all()
            history.update(created_at=timezone.localtime(trip.created_at), updated_at=timezone.localtime(trip.updated_at))
            return render(request, 'admin/history/expenseorderhistory.html', {'history': history})
        except expensemodel.DoesNotExist:
            request.session['error'] = 'Expense not found'
            return render(request, 'admin/history/expenseorderhistory.html', {'error': 'Expense not found'})
        except Exception as e:
            request.session['error'] = str(e)
            return render(request, 'admin/history/expenseorderhistory.html', {'error': str(e)})
    else:
        return redirect('login')

def delexpensehistory(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            if 'ser1' in request.POST:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')

                if not (frdate or todate or code != '--------------------Select-------------------'):
                    return render(request, 'admin/history/delexpensehistory.html', {'code': isa_trucks})

                filters = {}

                if code != '--------------------Select-------------------':
                    filters['code'] = code

                if frdate and todate:
                    filters['date__range'] = [frdate, todate]

                expense = expensemodel.history.filter(**filters,history_type__in=['-']).order_by('date')

                return render(request, 'admin/history/delexpensehistory.html',
                                {'expenses': expense, 'code': isa_trucks})
        return render(request, 'admin/history/delexpensehistory.html', {'code': isa_trucks})
    else:
        return redirect('login')

def delexpenseorderhistory(request, id):
    if 'username' in request.session:
        try:
            history = expensemodel.history.filter(id=id)
            return render(request, 'admin/history/delexpenseorderhistory.html', {'history': history})
        except expensemodel.DoesNotExist:
            request.session['error'] = 'Expense not found'
            return render(request, 'admin/history/delexpenseorderhistory.html', {'error': 'Expense not found'})
        except Exception as e:
            request.session['error'] = str(e)
            return render(request, 'admin/history/delexpenseorderhistory.html', {'error': str(e)})
    else:
        return redirect('login')

def mileage(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and ( code == '' or code == '----------------------------------Select---------------------------------------'):
                    return render(request, 'admin/ISA/mileage.html', {'code': isa_trucks})
                if not code or code == '----------------------------------Select---------------------------------------':
                    filter_kwargs = {}
                else:
                    filter_kwargs = {'code': code}

                if frdate and todate:
                    filter_kwargs['dat__range'] = [frdate, todate]

                trips = tripmodel.objects.filter(**filter_kwargs).order_by('dat')
                if trips.exists():
                    combined_data = []
                    for trip in trips:
                        trans_data = truckmodel.objects.filter(code=trip.code, trans='ISA').first()
                        if trans_data:
                            distance = trip.clkm-trip.opkm
                            mileage = int(distance) / trip.disqnt if trip.disqnt != 0 else 0
                            combined_data.append({'trip': trip, 'batta': batta, 'trans': trans_data, 'mileage': mileage,
                                                      'distance':distance})
                    return render(request, 'admin/ISA/mileage.html', {'ser1': combined_data, 'code': isa_trucks})
                else:
                    messages.error(request, 'No trips found.')
                    return render(request, 'admin/ISA/mileage.html', {'code': isa_trucks})
            except tripmodel.DoesNotExist:
                messages.error(request, 'No trips found.')
                return render(request, 'admin/ISA/mileage.html', {'code': isa_trucks})
        return render(request, 'admin/ISA/mileage.html', {'code': isa_trucks})
    else:
        return redirect('login')

def isaprofit(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if 'ser1' in request.POST:
            try:
                frdate = request.POST.get('frdate')
                todate = request.POST.get('todate')
                code = request.POST.get('code')
                if (not frdate or frdate == '') and (not todate or todate == '') and (code == '' or code == '----------------------------------Select---------------------------------------'):
                    return render(request, 'admin/ISA/isaprofit.html', {'code': isa_trucks})

                if not code or code == '----------------------------------Select---------------------------------------':
                    trips = tripmodel.objects.all().order_by('dat')
                    if frdate and todate:
                        trips = trips.filter(dat__range=[frdate, todate])
                else:
                    trips = tripmodel.objects.filter(code=code).order_by('dat')
                    if frdate and todate:
                        trips = trips.filter(dat__range=[frdate, todate])
                combined_data=[]
                total_hire = 0
                total_discount = 0
                total_batta = 0
                total_exp = 0
                total_com=0
                if trips.exists():
                    for trip in trips:
                        trans_data = truckmodel.objects.filter(code=trip.code, trans='ISA').first()
                        if trans_data:
                            hire = 0
                            hire+=trip.hire+trip.halt
                            profit=hire-trip.dis-trip.amount-trip.exptotal-trip.com
                            combined_data.append({'trip': trip,'bill': hire,'profit': profit})
                            total_hire += hire
                            total_exp += trip.exptotal
                            total_discount += trip.dis
                            total_batta+=trip.amount
                            total_com+=trip.com
                    total_profit = total_hire - total_discount - total_batta - total_exp - total_com
                    return render(request, 'admin/ISA/isaprofit.html', {
                        'total_profit': total_profit,
                        'total_hire': total_hire,
                        'ser1': combined_data,
                        'code': isa_trucks,
                        'total_dis': total_discount,
                        'total_batta': total_batta,
                        'total_exp': total_exp,
                        'total_com': total_com
                    })
                else:
                    messages.error(request, 'No data found.')
                    return render(request, 'admin/ISA/isaprofit.html', {'code': isa_trucks})
            except tripmodel.DoesNotExist:
                messages.error(request, 'No trips found.')
                return render(request, 'admin/ISA/isaprofit.html', {'code': isa_trucks})
        return render(request, 'admin/ISA/isaprofit.html', {'code': isa_trucks})
    else:
        return redirect('login')

def fullstaffview(request):
    if 'username' in request.session:
        isa_trucks = truckmodel.objects.filter(trans='ISA')
        if request.method == 'POST':
            diesel = 0
            hire = 0
            halt = 0
            com=0
            frdate = request.POST.get('frdate')
            todate = request.POST.get('todate')
            code = request.POST.get('code')
            if (not frdate or frdate == '') and (not todate or todate == '') and (
                    code == '' or code == '----------------------------------Select---------------------------------------'):
                return render(request, 'staff/reports/fullstaffview.html', {'code': isa_trucks})
            filter_kwargs = {}

            if code and code != '----------------------------------Select---------------------------------------':
                filter_kwargs['code'] = code

            if frdate and todate:
                filter_kwargs['dat__range'] = [frdate, todate]

            trips = tripmodel.objects.filter(**filter_kwargs).order_by('dat')
            if trips.exists():
                combined = []
                bata = lift = print = othexp = wei = halts = park = rto = adv = loan = total = roro = adblue = oil = insur = 0
                tax = emi = test = work = spare = toll = rethread = bal = 0
                for trip in trips:
                    profit = trip.hire - trip.halt - trip.dis - trip.amount - trip.exptotal - trip.com - trip.buy
                    bal += profit
                    distance = trip.clkm - trip.opkm
                    mileage = int(distance) / trip.disqnt if trip.disqnt != 0 else 0
                    batta = battamodel.objects.filter(pk=trip.battaid)
                    for batta in batta:
                        bata += batta.batta
                        lift += batta.lift
                        print += batta.print
                        othexp += batta.othexp
                        wei += batta.wei
                        halts += batta.halt
                        park += batta.park
                        rto += batta.rto
                        adv += batta.adv
                        loan += batta.loan
                        total += batta.total
                    exp = expensemodel.objects.filter(pk=trip.expid)
                    for exp in exp:
                        roro += exp.roro
                        adblue += exp.adblue
                        oil += exp.oil
                        insur += exp.insur
                        tax += exp.tax
                        emi += exp.emi
                        test += exp.test
                        work += exp.work
                        spare += exp.spare
                        toll += exp.toll
                        rethread += exp.rethread
                    diesel += trip.dis
                    halt += trip.halt
                    hire += trip.hire
                    com += trip.com
                    combined.append({'trip': trip, 'batta': batta, 'exp': exp, 'profit': profit, 'mileage': mileage})

            if 'ser1' in request.POST:

                return render(request, 'staff/reports/fullstaffview.html', {'trip': combined, 'halt': halt,
                                'diesel': diesel, 'hire': hire,'bata':bata,'lift':lift,'print':print,'othexp':othexp,'wei':wei,
                                'halts':halts,'park':park,'rto':rto,'adv':adv,'loan':loan,'total':total,'roro':roro,'code': isa_trucks,
                                'adblue':adblue,'oil':oil,'insur':insur,'tax':tax,'emi':emi,'test':test,'work':work,'spare':spare,
                                'toll':toll,'rethread':rethread,'bal':bal,'com':com})

            if 'export' in request.POST:
                html = render_to_string('staff/reports/fullreport.html',{'trip': combined, 'diesel': diesel,
                                'hire': hire, 'total': total,'halt': halt,'bata':bata,'lift':lift,'print':print,'othexp':othexp,
                                'halts':halts,'park':park,'rto':rto,'adv':adv,'loan':loan,'total':total,'roro':roro,'wei':wei,
                                'adblue':adblue,'oil':oil,'insur':insur,'tax':tax,'emi':emi,'test':test,'work':work,'spare':spare,
                                'toll':toll,'rethread':rethread,'bal':bal,'com':com})
                wb = Workbook()
                ws = wb.active
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table')
                rows = table.find_all('tr')
                # Download the image

                row_idx = 1  # Initialize row index

                for row in rows:
                    cells = row.find_all('td')
                    for i, cell in enumerate(cells):
                        value = cell.text
                        if value.replace('.', '', 1).replace('-', '', 1).isdigit():  # Check if value is a number
                            ws.cell(row=row_idx, column=i + 1).value = float(value)
                            if float(value) < 0:
                                ws.cell(row=row_idx, column=i + 1).value = float(value)
                                ws.cell(row=row_idx, column=i + 1).number_format = '#,##0.00;[Red]-#,##0.00'
                            else:
                                ws.cell(row=row_idx, column=i + 1).value = float(value)
                                ws.cell(row=row_idx, column=i + 1).number_format = '#,##0.00'
                        else:
                            ws.cell(row=row_idx, column=i + 1).value = value
                        if row_idx == 1:  # Assuming the heading is in the first row
                            ws.cell(row=row_idx, column=i + 1).font = Font(bold=True)
                    row_idx += 1  # Increment row index

                # Save Excel workbook to a file
                wb.save('fullreport.xlsx')

                # Return Excel file as a response
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'filename="fullreport.xlsx"'
                wb.save(response)
                return response
        return render(request, 'staff/reports/fullstaffview.html', {'code': isa_trucks})
    else:
        return redirect('login')
