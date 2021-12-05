from django.shortcuts import render,HttpResponse
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
from .algorithms.GetCurretntStatus import MyCurrentStatus
from .algorithms.GetClinicalReports import GetClinicalReports
from .algorithms.UserResultsPerfomance import UserFinaleports
import subprocess
from django.conf import settings

import matplotlib
#matplotlib.use("Agg")
# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHome.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})
def UserHome(request):
    return render(request, 'users/UserHome.html', {})

def CovidCurrentStatus(request):
    obj = MyCurrentStatus()
    obj.startCurrentStatus()
    filepath = settings.MEDIA_ROOT+"\\"+'coviddata.csv'
    import pandas as pd
    df = pd.read_csv(filepath)
    df = df[['state','positive','negative','pending','totalTestResults','hospitalizedCurrently','recovered','checkTimeEt','death','total']]
    df = df.to_html
    return render(request,'users/CovidCurrentData.html',{'data':df})

def UserClinicalDataReports(request):
    obj = GetClinicalReports()
    df = obj.startClinicalReports()

    return render(request,'users/UserClinicalData.html',{'data':df})

def UserChestXrayAnalysis(request):
    prog = "python keras-covid-19/train_covid19.py --dataset keras-covid-19/dataset"
    #subprocess.call(prog)
    return render(request,"users/UserCovidXreayimages.html",{})

def UserResults(request):
    obj = UserFinaleports()
    trainScore,testScore = obj.starProcess()
    return render(request,"users/UserLstmResults.html",{'trainScore':trainScore,'testScore':testScore})