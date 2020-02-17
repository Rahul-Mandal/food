from django.contrib import messages
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_text
import arrow
from cryptography.fernet import Fernet
from django.shortcuts import render, redirect
from .models import employeedetails, employee_attendance, employee_personaldetails, employee_educationaldetails, employee_experiencedetails,applied_leaves, weeklyactivity,admin1
from django.http import HttpResponse
import datetime
from cryptography import fernet
from datetime import date,datetime
from django.core.mail import send_mail
from django.db import connection
from cloudsolv import settings
cur=connection.cursor()
# Create your views here.

def signup(request):
    if request.method == 'GET':
        return render(request,'signup.html')
    if request.method == 'POST':
        empid1=request.POST['empid']
        empname1=request.POST['empname']
        email1=request.POST['email']
        password1=request.POST['pass1']
        password2=request.POST['pass2']
        if password1 == password2:
            if employeedetails.objects.filter(employee_email=email1,employee_id=empid1).exists():
                messages.add_message(request, messages.SUCCESS, "User with this id or email already exists")
                return redirect('/Signup/')
            else:
                p=str(password1)
                f=Fernet(settings.ENCRYPT_KEY)
                enctext=f.encrypt(p.encode('ascii'))
                encrypted_text = base64.urlsafe_b64encode(enctext).decode("ascii")
                form=employeedetails(employee_id=empid1, employee_name=empname1, employee_email=email1, employee_password=encrypted_text)
                try:
                    form.full_clean()
                    form.save()
                    messages.add_message(request, messages.SUCCESS, "succesfully signedup")
                    return redirect("/")
                except:
                    messages.add_message(request, messages.SUCCESS, "User with this id or email already exists")
                    return redirect('/Signup/')
        else:
            messages.info(request,'password not matching')
            return redirect('/Signup/')
    else:
        return HttpResponse("registration failed")

def login(request):
    if 'user' in request.session:
        return render(request,'dashboard.html')
    else:
        if request.method == 'GET':
            return render(request,'login1.html')
        if request.method=='POST':
            us=request.POST['id']
            pw1=request.POST['password']
            try:
                if employeedetails.objects.get(employee_id=us):
                    emp=employeedetails.objects.get(employee_id=us)
                    pw=emp.employee_password
                    txt = base64.urlsafe_b64decode(pw)
                    f = Fernet(settings.ENCRYPT_KEY)
                    decoded_text = f.decrypt(txt).decode("ascii")
                    if decoded_text == pw1:
                        request.session['user']={'id':us}
                        messages.add_message(request, messages.WARNING, "Logged in succesfully")
                        return render(request,'dashboard.html',{'session':request.session['user']})
                    else:
                        messages.add_message(request, messages.WARNING, "Please enter correct password")
                        return redirect('/')
                else:
                    messages.add_message(request, messages.WARNING, "Please Provide valid details")
                    return redirect('/')
            except:
                messages.add_message(request, messages.WARNING, "Please Provide valid details")
                return redirect('/')

def weeklyactivity1(request):
    if 'user' in request.session:
        if request.method == 'GET':
            employee1 = employeedetails.objects.get(employee_id=int(request.session['user']['id']))
            table = weeklyactivity.objects.all()
            no=table.count()
            if  no<=5:
                table1 = weeklyactivity.objects.all()
                return render(request, 'weeklyactivitytable.html', {'table': table1})
            else:
                days=['monday','tuesday','wednesday','thursday','friday']
                for day in days:
                    qs=weeklyactivity.objects.create(employee=employee1,week=day)
                    qs.save()
                table1=weeklyactivity.objects.all()
                return render(request,'weeklyactivitytable.html',{'table':table1})
        if request.method == 'POST':
            d=request.POST['day']
            a=request.POST['text']
            g=request.POST['goal']
            myweek=weeklyactivity.objects.get(week=d)
            myweek.activity=a
            myweek.goal = g
            myweek.save()
            request.method='GET'
            return redirect('/weeklyactivity/')

def experiencedetails(request):
    if 'user' in request.session:
        if request.method == 'GET':
            try:
                qs = employee_experiencedetails.objects.get(employee__employee_id=int(request.session['user']['id']))
                emp = employeedetails.objects.get(employee_id=int(request.session['user']['id']))
                return render(request,'saveexperience.html',{'qs':qs,'emp':emp})
            except:
                emp = employeedetails.objects.get(employee_id=int(request.session['user']['id']))
                return render(request,'expriencedetails.html', {'emp':emp})

        if request.method == 'POST':
            name=request.POST['orgo']
            p_sition = request.POST['p_osition']
            p_work= request.POST['p_work']
            salary= request.POST['salary']
            t_experience=request.POST['Total']
            ur_letter=request.FILES['Reliving']
            up_slip=request.FILES['Pay']
            employee = employeedetails.objects.get(employee_id=request.session['user']['id'])
            qs = employee_experiencedetails(name_of_organisation=name, job_role=p_sition, period_of_work=p_work, package=salary,employee=employee,total_experience=t_experience,relieving_letter=ur_letter,pay_slip=up_slip)
            qs.save()

            if "qs6" in request.FILES:
                if request.FILES['qs6'] is not None:
                    qs.is_form_any_uploaded=True
                    form=request.FILES['qs6']
                    qs.forms_any=form
                    qs.save()

            if 'orgo1' in request.POST:
                org = request.POST['orgo1']
                qs.name_of_organisation1 = org
                qs.save()

            if 'p_osition1' in request.POST:
                posi = request.POST['p_osition1']
                qs.job_role1 = posi
                qs.save()

            if 'p_work1' in request.POST:
                pwor = request.POST['p_work1']
                qs.period_of_work1 = pwor
                qs.save()

            if 'salary1' in request.POST:
                sala= int(request.POST['salary1'])
                qs.package1 = sala
                qs.save()

            if 'Total1' in request.POST:
                if request.POST['Total1'] != '':
                    totl= request.POST['Total1']
                    qs.total_experience1 = totl
                    qs.save()

            if 'Reliving1' in request.FILES:
                if request.FILES['Reliving1'] is not None:
                    qs.is_relivingletter_uploaded=True
                    reli = request.FILES['Reliving1']
                    qs.relieving_letter1 = reli
                    qs.save()

            if 'Pay1' in request.FILES:
                if request.FILES['Pay1' ] is not None:
                    qs.is_pay_slip1=True
                    reli = request.FILES['Pay1' ]
                    qs.relieving_letter1 = reli
                    qs.save()
            if "qss" in request.FILES:
                if request.FILES['qss'] is not None:
                    qs.is_form_any_uploaded1=True
                    qs.forms_any1=request.POST['qss']
                    qs.save()
            messages.add_message(request, messages.WARNING, "experience details saved successfully!")
            return render(request, 'dashboard.html')


def editexperiencedetails(request):
    if request.method == 'GET':
        qs = employee_experiencedetails.objects.get(employee__employee_id=int(request.session['user']['id']))
        return render(request, 'editexpriencedetails.html', {'qs': qs})

def updateexperiencedetails(request):
    if 'user' in request.session:
        name=request.POST['orgo']
        position=request.POST['p_osition']
        period_of_work=request.POST['p_work']
        salary=request.POST['salary1']
        Total_exp=request.POST['Total']
        employ=employeedetails.objects.get(employee_id=request.session['user']['id'])
        qs=employee_experiencedetails.objects.get(employee=employ)
        if qs:
            qs.name_of_organisation=name
            qs.job_role=position
            qs.period_of_work=period_of_work
            qs.package=salary
            qs.total_experience=Total_exp
            if 'Reliving2' in request.FILES:
                if request.FILES["Reliving2"] is not None:
                    reliving_letter=request.FILES['Reliving2']
                    qs.relieving_letter=reliving_letter
                    qs.save()
            if 'P' in request.FILES:
                if request.FILES['P'] is not None:
                    payslipp=request.FILES['P']
                    qs.pay_slip=payslipp
                    qs.save()
            if "qs6" in request.FILES:
                if request.FILES["qs6"] is not None:
                    form = request.FILES['qs6']
                    qs.is_form_any_uploaded=True
                    qs.forms_any=form
                    qs.save()

            if 'orgo1' in request.POST:
                if request.POST['orgo1'] != None:
                    name1 = request.POST['orgo1']
                    qs.name_of_organisation1=name1
                    qs.save()
            if 'p_osition1' in request.POST:
                if request.POST['p_osition1'] != None:
                    popsition1 = request.POST['p_osition1']
                    qs.job_role1=popsition1
                    qs.save()

            if 'p_work1' in request.POST:
                if request.POST['p_work1'] != None:
                    period_of_work1 = request.POST['p_work1']
                    qs.period_of_work1=period_of_work1
                    qs.save()

            if 'salary11' in request.POST:
                if request.POST['salary11'] != '':
                    salary1 = int(request.POST['salary11'])
                    qs.package1 = salary1
                    qs.save()

            if 'Total1' in request.POST:
                if request.POST['Total1'] != None:
                    total1 = request.POST['Total1']
                    qs.total_experience1 = total1
                    qs.save()

            if 'R1' in request.FILES:
                if request.FILES['R1'] != None:
                    total1 = request.FILES['R1']
                    qs.is_relivingletter_uploaded=True
                    qs.relieving_letter1 = total1
                    qs.save()
            if 'P1' in request.FILES:
                if request.FILES['P1'] != None:
                    total1 = request.FILES['P1']
                    qs.is_pay_slip1=True
                    qs.is_pay_slip1 = total1
                    qs.save()
            if 'qss' in request.FILES:
                if request.FILES['qss'] != None:
                    total1 = request.FILES['qss']
                    qs.is_form_any_uploaded1=True
                    qs.forms_any1 = total1
                    qs.save()
            qs.save()
            return redirect('/dashboard/')


def educationdetails(request):
    if 'user' in request.session:
        if request.method == 'GET':
            try:
                qs = employee_educationaldetails.objects.get(employee__employee_id=int(request.session['user']['id']))
                return render(request,'savededucationaldetails.html',{'qs':qs})
            except:
                return render(request,'education_details.html')
        if request.method == 'POST':
            employ=employeedetails.objects.get(employee_id=int(request.session['user']['id']))
            x_name = request.POST['High']
            x_board = request.POST['Hboard']
            x_per = request.POST['Spercentage']
            x2_name = request.POST['Inter']
            x2_board = request.POST['Board1']
            x2_per = request.POST['Ipercentage']
            gra_name = request.POST['Graduation']
            gra_board = request.POST['Gboard']
            gra_per = request.POST['Gpercentage']
            education = employee_educationaldetails(tenth_schoolname=x_name, tenth_schoolboard=x_board,tenth_percentage=x_per,inter_collegename=x2_name, inter_board=x2_board,inter_percentage=x2_per, graduation_collegename=gra_name, graduation_board=gra_board,graduation_percentage=gra_per,employee=employ)
            education.save()
            if 'PGraduation' in request.POST:
                if request.POST['PGraduation'] is not None:
                    pgcollege=request.POST['PGraduation']
                    education.postgraduation_collegename=pgcollege
                    education.save()
            if 'PGboard' in request.POST:
                if request.POST['PGboard'] is not None:
                    pgboard=request.POST['PGboard']
                    education.postgraduation_board=pgboard
                    education.save()
            if 'P' in request.POST:
                if request.POST['P'] is not None:
                    post_graduation_percentage=request.POST['P']
                    education.postgraduation_percentage=post_graduation_percentage
                    education.save()
            if "PGraduation1" in request.FILES:
                if request.FILES["PGraduation1"] is not None:
                    pgcert=request.FILES['PGraduation1']
                    education.is_post_graduationcertificate_uploaded=True
                    education.postgraduation_cerificate=pgcert
                    education.save()
            if "high1" in request.FILES:
                if request.FILES["high1"] is not None:
                    x_cert = request.FILES['high1']
                    education.tenth_cerificate=x_cert
                    education.save()
            if "inter1" in request.FILES:
                if request.FILES["inter1"] is not None:
                    x2_cert = request.FILES["inter1"]
                    education.inter_cerificate=x2_cert
                    education.save()

            if "Graduation1" in request.FILES:
                if request.FILES["Graduation1"] is not None:
                    gra_cert = request.FILES["Graduation1"]
                    education.graduation_cerificate = gra_cert
                    education.save()
            messages.add_message(request, messages.SUCCESS, "post graduation details saved succesfully!")
            return render(request,"dashboard.html")
def editeducationaldetails(request):
    if request.method == 'GET':
        qs = employee_educationaldetails.objects.get(employee__employee_id=int(request.session['user']['id']))
        return render(request, 'editeducation_details.html', {'qs': qs})

def updateeducationaldetails(request):
    if 'user' in request.session:
        if request.method == 'POST':
            employee = employeedetails.objects.get(employee_id=request.session['user']['id'])
            x_name = request.POST['High']
            x_board = request.POST['Hboard']
            x_per = request.POST['Spercentage']
            x2_name = request.POST['Inter']
            x2_board = request.POST['Board1']
            x2_per = request.POST['Ipercentage']
            gra_name = request.POST['Graduation']
            gra_board = request.POST['Gboard']
            gra_per = request.POST['Gpercentage']
            qs=employee_educationaldetails.objects.get(employee__employee_id=(request.session['user']['id']))
            if qs:
                qs.employee =employee
                qs.tenth_schoolname =x_name
                qs.tenth_schoolboard=x_board
                qs.tenth_percentage=x_per
                qs.inter_collegename = x2_name
                qs.inter_board = x2_board
                qs.inter_percentage = x2_per
                qs.graduation_collegename = gra_name
                qs.grad_board = gra_board
                qs.graduation_percentage = gra_per
                if 'PGraduation' in request.POST:
                    if request.POST['PGraduation'] is not None:
                        pgcollege = request.POST['PGraduation']
                        qs.postgraduation_collegename = pgcollege
                        qs.save()
                if 'PGboard' in request.POST:
                    if request.POST['PGboard'] is not None:
                        pgboard = request.POST['PGboard']
                        qs.postgraduation_board = pgboard
                        qs.save()
                if 'P' in request.POST:
                    if request.POST['P'] is not None:
                        post_graduation_percentage = request.POST['P']
                        qs.postgraduation_percentage = post_graduation_percentage
                        qs.save()
                if "PGraduation1" in request.FILES:
                    if request.FILES["PGraduation1"] is not None:
                        pgcert = request.FILES['PGraduation1']
                        qs.is_post_graduationcertificate_uploaded = True
                        qs.postgraduation_cerificate = pgcert
                        qs.save()
                if "high1" in request.FILES:
                    if request.FILES["high1"] is not None:
                        x_cert = request.FILES['high1']
                        qs.tenth_cerificate = x_cert
                        qs.save()
                if "inter1" in request.FILES:
                    if request.FILES["inter1"] is not None:
                        x2_cert = request.FILES["inter1"]
                        qs.inter_cerificate = x2_cert
                        qs.save()

                if "Graduation1" in request.FILES:
                    if request.FILES["Graduation1"] is not None:
                        gra_cert = request.FILES["Graduation1"]
                        qs.graduation_cerificate = gra_cert
                        qs.save()
                messages.add_message(request, messages.SUCCESS, "post graduation details updated succesfully!")
                return redirect('/dashboard/')


def personaldetails(request):
    if 'user' in request.session:
        if request.method == 'GET':
            try:
                qs = employee_personaldetails.objects.get(employee__employee_id=int(request.session['user']['id']))
                emp=employeedetails.objects.get(employee_id=int(request.session['user']['id']))
                request.session['image'] = qs.employee_image.url
                return render(request, 'saved_Personal.html', {'qs': qs, 'emp':emp})
            except:
                emp=employeedetails.objects.get(employee_id=int(request.session['user']['id']))
                return render(request, 'personaldetails.html',{'emp':emp})
        if request.method == 'POST':
            emp_image=request.FILES['qs']
            desig = request.POST['e_desig']
            jng_date=request.POST['j_date']
            dob = request.POST['f_dob']
            addr = request.POST['address1']
            gendr = request.POST['gender']
            m_status = request.POST['Mstatus']
            city = request.POST['city']
            state = request.POST['state']
            mobile = int(request.POST['Mobile'])
            relative = request.POST['r_name']
            mno = int(request.POST['m_no'])
            pan = request.POST['Pan']
            aadhar = request.POST['aadhar']
            code = int(request.POST['Code'])
            if 'qs4' not in request.FILES:
                messages.add_message(request, messages.WARNING, "please upload aadhar,saving failed!")
                return redirect('/personal/')
            if 'qs1' not in request.FILES:
                messages.add_message(request, messages.WARNING, "please upload pancard,saving failed!")
                return redirect('/personal/')
            else:
                aadhar_image=request.FILES['qs4']
                pan_image=request.FILES['qs1']
                emp = employeedetails.objects.get(employee_id=int(request.session['user']['id']))
                qs = employee_personaldetails( joining_date=jng_date, designation=desig, empoyee_dob=dob,employee_image=emp_image,
                                              gender=gendr, maritial_status=m_status, Address1=addr,
                                                aadhar_number=aadhar,upload_aadhar=aadhar_image,upload_pancard=pan_image,
                                              pan_number=pan,
                                             city=city, state=state,
                                              postal_code=code, mobile_number=mobile, relatives_name=relative,
                                                relative_mobile_number=mno,employee=emp)
                qs.save()

                if 'address2' in request.POST:
                    address=request.POST['address2']
                    qs.Address1=address
                    qs.save()
                if 'fa_name' in request.POST:
                    fathername=request.POST['fa_name']
                    qs.father_name=fathername
                    qs.save()
                if request.POST['telephone'] != '':
                    tel = request.POST['telephone']
                    qs.telephone =tel
                    qs.save()
                if 'sp_name' in request.POST:
                    spname = request.POST['sp_name']
                    qs.spouse_name = spname
                    qs.save()
                if 'relation' in request.POST:
                    relation = request.POST['relation']
                    qs.relation=relation
                    qs.save()

                if request.POST['no_children'] != '':
                    chilldren = int(request.POST['no_children'])
                    qs.children=chilldren
                    qs.save()

                if 'Passport' in request.POST:
                    passport = request.POST['Passport']
                    qs.passport_number=passport
                    qs.save()
                if 'driving' in request.POST:
                    driving = request.POST['driving']
                    qs.drivinglicense_number=driving
                    qs.save()
                if 'qs3' in request.FILES:
                    if request.FILES['qs3'] is not None:
                        qs.is_drivinglicense_uploaded=True
                        qs.save()
                        driving_license= request.FILES['qs3']
                        qs.upload_drivinglicense = driving_license
                        qs.save()

                if 'raddress' in request.POST:
                    relative_address = request.POST['raddress']
                    qs.relative_address=relative_address
                    qs.save()

                if 'voter' in request.POST:
                    voter_id=request.POST['voter']
                    qs.voter_id_number=voter_id
                    qs.save()

                if 'qs5' in request.FILES:
                    if  request.FILES['qs5'] is not None:
                        qs.is_Voterid_uploaded=True
                        voter_id_image=request.FILES['qs5']
                        qs.upload_voterid=voter_id_image
                        qs.save()
                if 'qs2' in request.FILES:
                    if request.FILES['qs2'] is not None:
                        qs.is_passport_uploaded=True
                        passport_image=request.FILES['qs2']
                        qs.upload_passport=passport_image
                        qs.save()
                if 'address2' in request.POST:
                     add2=request.POST['address2']
                     qs.Address2=add2
                     qs.save()
                if 'p_no' in request.POST:
                    if request.POST['p_no'] != '':
                         relative_phone=int(request.POST['p_no'])
                         qs.phone_number=relative_phone
                         qs.save()
                messages.add_message(request, messages.SUCCESS, "Personal details saved suceesfully")
                return HttpResponse('success')
    else:
        return render(request,'login.html')

def editpersonaldetails(request):
    if request.method == 'GET':
        qs = employee_personaldetails.objects.get(employee__employee_id=int(request.session['user']['id']))
        return render(request, 'editpersonaldetails.html', {'qs': qs})
def updatepersonaldetails(request):
    if 'user' in request.session:
        if request.method == 'POST':
            employee = employeedetails.objects.get(employee_id=request.session['user']['id'])
            #e_id = request.POST['f_id']
            #e_name = request.POST['f_name']
            jng_date = request.POST['j_date']
            desig = request.POST['e_desig']
            dob = request.POST['f_dob']
            fathername = request.POST['fa_name']
            gendr = request.POST['gender']
           # email = request.POST['e_mail']
            m_status = request.POST['Mstatus']
            spname = request.POST['sp_name']
            city = request.POST['city']
            state = request.POST['state']
            mobile = int(request.POST['Mobile'])
            relative = request.POST['r_name']
            relation = request.POST['relation']
            relative_add = request.POST['raddress']
            mno = int(request.POST['m_no'])
            pan = request.POST['Pan']
            passp = request.POST['Passport']
            vote= request.POST['voter']
            aadhar= request.POST['aadhar']
            driving= request.POST['driving']
            addr = request.POST['address1']
            address = request.POST['address2']

            qs=employee_personaldetails.objects.get(employee=employee)
            if qs:
                qs.employee =employee
                qs.joining_date=jng_date
                qs.designation=desig
                qs.employee_dob=dob
                qs.father_name = fathername
                qs.gender = gendr
                qs.maritial_status =m_status
                qs.spouse_name = spname
                qs.city = city
                qs.state  = state
                qs.mobile_number = mobile
                qs.relatives_name= relative
                qs.relation = relation
                qs.relative_address = relative_add
                qs.relative_mobile_number =mno
                qs.pan_number=pan
                qs.passport_number=passp
                qs.voter_id_number=vote
                qs.drivinglicense_number=driving
                qs.aadhar_number=aadhar
                qs.Address1=addr
                qs.Address2=address
                qs.save()
                if request.POST['no_children'] != '':
                    qs.children=request.POST['no_children']
                    qs.save()
                else:
                    qs.children=None
                    qs.save()
                if request.POST['telephone'] != '':
                    qs.telephone = request.POST['telephone']
                    qs.save()
                else:
                    qs.telephone=None
                    qs.save()

                if request.POST['p_no'] != '':
                    qs.phone_number = request.POST['p_no']
                    qs.save()
                else:
                    qs.phone_number=None
                    qs.save()
                if 'qs' in request.FILES:
                    emp_image = request.FILES['qs']
                    qs.employee_image=emp_image
                    qs.save()
                if 'qs4' in request.FILES:
                    emp_image = request.FILES['qs4']
                    qs.upload_aadhar = emp_image
                    qs.save()
                if 'qs1' in request.FILES:
                    emp_image = request.FILES['qs1']
                    qs.upload_pancard = emp_image
                    qs.save()

                if 'qs5' in request.FILES:
                    if request.FILES['qs5'] is not None:
                        qs.is_Voterid_uploaded = True
                        voter_id_image = request.FILES['qs5']
                        qs.upload_voterid = voter_id_image
                        qs.save()
                if 'qs2' in request.FILES:
                    if request.FILES['qs2'] is not None:
                        qs.is_passport_uploaded = True
                        passport_image = request.FILES['qs2']
                        qs.upload_passport = passport_image
                        qs.save()

                if 'qs3' in request.FILES:
                    if request.FILES['qs3'] is not None:
                        qs.is_drivinglicense_uploaded = True
                        passport_image = request.FILES['qs3']
                        qs.upload_drivinglicense = passport_image
                        qs.save()


                return HttpResponse("updated succesfully")
            else:
                return HttpResponse("please enter valid details")

def monthlyattendance(request):
    if request.method == 'GET':
        return render(request,'monthlyat.html')
    if request.method == 'POST':
        mon=str(request.POST['month'])
        x=mon.split('-')
        l=x[1]
        attendance = employee_attendance.objects.filter(employee__employee_id=int(request.session['user']['id']),login_date__month=l)
        return render(request, 'attendence.html', {'attendance': attendance})

def requestleave(request):
    if 'user' in request.session:
        if request.method == 'GET':
            return render(request,'requestleave.html')
        if request.method == 'POST':
            reason=request.POST['r_leave']
            fr_date=request.POST['f_date']
            to_date=request.POST['t_date']
            f=arrow.get(fr_date)
            t=arrow.get(to_date)
            daysdiff = (t -f)
            noofdays1=daysdiff.days+1
            emp=employeedetails.objects.get(employee_id=int(request.session['user']['id']))
            #emp1=employee_personaldetails.objects.get(employee__employee_id=int(request.session['user']['id']))
            leave=applied_leaves(reason=reason,from_date=fr_date,to_date=to_date,applied_by=emp,no_of_days=noofdays1)
            leave.save()
            subject="Hello Prathysha ma'am , This is "+emp.employee_name+". I want leave from " +fr_date+ " to " +to_date+" for "+str(noofdays1)+ " day(s)  due to "+reason+  ". Could you please grant me leave. "
            send_mail(
                emp.employee_name
                ,
                subject,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER]
            )
            messages.add_message(request, messages.WARNING, "leave request has been sent")
            return redirect('/request/')

def dashboard(request):
    if 'user' in request.session:
        if request.method == 'GET':
            return render(request,'dashboard.html')

def Viewmyleaves(request):
    if 'user' in request.session:
        if request.method == 'GET':
            leaves=applied_leaves.objects.filter(applied_by__employee_id=request.session['user']['id'])
            return render(request,'myleave.html',{'employees':leaves})



def myattendance(request):
    if request.method == 'GET':
        today = date.today()
        month = today.month
        attendance=employee_attendance.objects.filter(employee__employee_id=int(request.session['user']['id']),login_date__month=month)
        return render(request,'attendence.html',{'attendance':attendance})
    cur.close()
    connection.close()

def forgot_password(request):
    if request.method == 'GET':
        return render(request,'forgot_password.html')
    if request.method == 'POST':
        employeeid=request.POST['id']
        employeeemail = request.POST['email']
        #try:
        employee_data=employeedetails.objects.get(employee_id=int(employeeid),employee_email=employeeemail)
        pw=employee_data.employee_password
        txt = base64.urlsafe_b64decode(pw)
        f = Fernet(settings.ENCRYPT_KEY)
        decoded_text = f.decrypt(txt).decode("ascii")
        subject = "hello " + employee_data.employee_name+ "   your password is " +"  "+ decoded_text + "    "+"Don't Share this with anyone,Thankyou "
        send_mail(
            "Cloudsolv Account Password!"
            ,
            subject,
            settings.EMAIL_HOST_USER,
            [employee_data.employee_email]
        )
        messages.add_message(request, messages.WARNING, "password was sent to your registered mail id")
        return redirect('/')
        #except:
            #messages.add_message(request, messages.WARNING, "Please Enter Valid Details!")
            #return redirect('/forgot/')


def logout(request):
    if request.method=='GET':
        del request.session['user']
        messages.add_message(request, messages.SUCCESS, "Logout Success!")
        return redirect('/')




def changepassword(request):
    if request.method=='GET':
        form = employeedetails.objects.filter(employee_id=request.session['user']['id'])
        return render(request, 'changepassword.html', {'forms': form})
    if request.method=='POST':
        try:
            emp=employeedetails.objects.get(employee_id=int(request.session['user']['id']))
            pw = emp.employee_password
            txt = base64.urlsafe_b64decode(pw)
            f = Fernet(settings.ENCRYPT_KEY)
            decoded_text = f.decrypt(txt).decode("ascii")
            pass1=request.POST['oldpass']
            if decoded_text == pass1:
                if request.POST['newpass'] == request.POST['confirmpass']:
                    new=request.POST['newpass']
                    p = str(new)
                    f = Fernet(settings.ENCRYPT_KEY)
                    enctext = f.encrypt(p.encode('ascii'))
                    encrypted_text = base64.urlsafe_b64encode(enctext).decode("ascii")
                    emp.employee_password=encrypted_text
                    emp.save()
                    messages.add_message(request, messages.SUCCESS, "password updated succesfully!")
                    return redirect('/dashboard/')
                else:
                    messages.add_message(request, messages.ERROR, "please enter a valid password")
                    return redirect('/changepsw/')
        except:
            messages.add_message(request, messages.ERROR, "please enter a valid password")
            return redirect('/changepsw/')

def mypayslips(request):
    if 'user' in request.session:
        if request.method == 'GET':
            employee = employeedetails.objects.get(employee_id=int(request.session['user']['id']))
            pay=employee_personaldetails.objects.filter(employee=employee)
            return render(request,'payslips.html',{'payslip':pay})

    else:
        return render(request,'login.html')








def admin(request):
    if request.method=='GET':
        return render(request,'adminlogin.html')
    if request.method=='POST':
        a=request.POST['name']
        b=request.POST['password']


        c=admin1.objects.filter(Username=a,Password=b)
        #form = employeedetails(employee_id=empid1, employee_name=empname1, employee_email=email1,

         #                      employee_password=encrypted_text)

        if c:
            #request.session['user'] = {'id': a, 'psw': b, }
            #emp = employee_personaldetails.objects.get(id=int(request.session['user']['id']))
            # return HttpResponse(emp.designation)
            return redirect('/adminpage')

        else:
            return HttpResponse('failed')

def adminpage(request):
    return render(request,'adminpage.html')


def adminleave(request):
    if request.method=='GET':
        a=applied_leaves.objects.all()
        return render(request,'adminleavestatus.html',{'qs':a})

def edit(request, id):
    employee = applied_leaves.objects.get(id=id)
    return render(request, 'edit.html', {'employee': employee})

def update(request,id):

    #form = EmployeeForm(request.POST, instance=employee)
    #if employee.is_valid():
    if request.method=='POST':
        employee = applied_leaves.objects.get(id=id)
        s=request.POST['choose']
        employee.status=s
        employee.save()
        return redirect('/adminleave/')
    else:
        return HttpResponse('sorry')
            #return render(request,'edit.html',{'employee':employee})



def status(request):
    if request.method=='GET':
        a=employeedetails.objects.all()
        #b=employee_personaldetails.objects.filter(employee__employee_id=((request.session['user']['id'])))
        return render(request,'companystatus.html',{'qs':a})


def profile(request):
    if request.method=='GET':
        a=admin1.objects.all()
        #b=employee_personaldetails.objects.filter(employee__employee_id=((request.session['user']['id'])))
        return render(request,'profile.html',{'qs':a})

def changeadmin(request):
    if request.method=='GET':
        return render(request, 'changeadmin.html')
    if request.method=='POST':
        form = admin1.objects.get(Password=request.POST['password'])
        if request.POST['newpass'] == request.POST['confirmpass']:
            form.Password=request.POST['newpass']
            form.save()
            return HttpResponse('success')
        else:
            return HttpResponse('sorry')


def adminpersonal(request):
    if request.method == 'GET':
        qs = employeedetails.objects.all()
        a=qs.count()
        #return HttpResponse(a)
        #emp=employeedetails.objects.get(id=id)
        return render(request, 'list.html',{'qs':a})

def adminlist(request):
    if request.method == 'GET':
        a= employeedetails.objects.filter()
        #a=qs.count()
        #return HttpResponse(a)
        #emp=employeedetails.objects.get(id=id)
        return render(request, 'list1.html',{'qs':a})

def admindoc(request):
    if request.method == 'GET':
        a= employee_personaldetails.objects.all()
        emp=employee_educationaldetails.objects.all()
        exp=employee_experiencedetails.objects.all()
        if employee_experiencedetails.objects.filter(pay_slip='aadhar_qVRol81'
                                                              '.PNG').exists():
            print('yes')
            return render(request, 'doc.html', {'qs': a, 'emp': emp, 'exp': exp})

        else:
            print('no')
            return render(request, 'doc.html',{'qs':a,'emp':emp,'exp':exp})

def Adminpersonal(request,employee__employee_id):
    if request.method == 'GET':
        qs1 = employee_personaldetails.objects.get(employee__employee_id=employee__employee_id)
        #emp = employeedetails.objects.get(employee_id=id)
        return render(request, 'AdminPersonal.html', {'qs': qs1})
    '''except:
                emp = employeedetails.objects.get(employee_id=id)
                return render(request, 'personaldetails.html', {'emp': emp})'''


