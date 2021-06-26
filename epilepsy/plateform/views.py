from django.http.response import HttpResponse
from django.shortcuts import render,redirect
from django.core.files.storage import FileSystemStorage
from .forms import Customerform, Edfform,CreateUserForm
from .models import Customer, Edf, Ica_image
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user,allowed_user,admin_only
from django.contrib.auth.models import Group,User
from django.core.mail import send_mail,EmailMultiAlternatives





@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            subject ="New Visitor in epilepsydetection.com"
            text_content = "Dear admin, you have a new Visitor name "+username+ ", to have more informations click "
            from_email = email
            to = ['hadrien.gayaptagheu@esprit.tn']

            send_mail_admin(subject=subject,text_content=text_content,from_email=from_email,to=to)

            messages.success(request,'Account successfull created as '+username)

            return redirect('login')
    
    context = {'form':form}

    return render(request,'plateform/register.html',context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username,password=password)

        if username is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Username Or Password is Incorrect')

    context = {}
    return render(request,'plateform/login.html',context)

@unauthenticated_user
def dashboard_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username,password=password)

        if username is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.info(request,'Username Or Password is Incorrect')

    context = {}
    return render(request,'plateform/login_admin.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def deleteUser(request,pk):
    user = User.objects.get(pk=pk)
    if(user.customer):
        user.customer.delete()
    else:
        user.delete()

    return redirect('dashboard_user')

@login_required(login_url='login')
@allowed_user(allowed_roles=['customer','admin'])
def customer_settings(request):
    customer = request.user.customer
    form = Customerform(instance=customer)
    context = {'form':form}

    if request.method == 'POST':
        form = Customerform(request.POST,instance=customer)
        if form.is_valid():
            form.save()
            return redirect('home')
            
    return render(request,'plateform/customer_settings.html',context)


@login_required(login_url='login')
def home(request):
    return render(request,'plateform/home.html')

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin','expert'])
def expert(request):
    if request.method =='POST':
        form = Edfform(request.POST,request.FILES)
        if form.is_valid() :
            edf = form.save(commit=False)
            edf.saveBy=request.user.customer
            edf.save()
            redirect('expert_edf_list',pk=request.user.customer.id)
    else:
        form = Edfform()
    
    return render(request,'plateform/expert.html',{
        'form':form
    })

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin','patient'])
def normal(request):
    print('yooooooooooooooooooooooooooooo')
    if request.method =='POST':
        form = Edfform(request.POST,request.FILES)
        if form.is_valid() :
            edf = form.save(commit=False)
            edf.saveBy=request.user.customer
            edf.save()
            redirect('normal_edf_list',pk=request.user.customer.id)
    else:
        form = Edfform()
    
    return render(request,'plateform/normal.html',{
        'form':form
    })

@allowed_user(allowed_roles=['admin','patient'])
@login_required(login_url='login')
def edf_normal_list(request,pk):
    customer = Customer.objects.get(pk=pk)
    edfs = Edf.objects.all().filter(saveBy=customer)
    return render(request,'plateform/normal_edf_list.html',{
        'Edfs':edfs
    })

@allowed_user(allowed_roles=['admin','expert'])
@login_required(login_url='login')
def edf_list(request,pk):
    customer = Customer.objects.get(pk=pk)
    edfs = Edf.objects.all().filter(saveBy=customer)
    return render(request,'plateform/expert_edf_list.html',{
        'Edfs':edfs
    })

@login_required(login_url='login')
def delete_edf(request,pk):
    if request.method == 'POST':
        edf = Edf.objects.get(pk=pk)
        edf.delete()

    return redirect('expert_edf_list')



@login_required(login_url='login')
def explore_edf(request):
    return render(request,'plateform/expert_explore.html')

@login_required(login_url='login')
@admin_only
def dashboard(request):
    customers = Customer.objects.all()
    total = customers.count()

    context =  {
        'total':total,
        'customers':customers
    }
    return render(request,'plateform/dashboard.html',context)

@login_required(login_url='login')
@admin_only
def dashboard_user(request):
    users = User.objects.all()
    total = users.count()


    context =  {
        'total':total,
        'users':users
    }
    return render(request,'plateform/dashboard_user.html',context)

@login_required(login_url='login')
@admin_only
def dashboard_edf(request):
    edfs =  Edf.objects.all()
    total_edf = edfs.count()

    icas = Ica_image.objects.all()
    total_ica = icas.count()

    context =  {
        'edfs':edfs,
        'total_edf':total_edf,
        'icas':icas,
        'total_ica':total_ica
    }
    return render(request,'plateform/dashboard_edf.html',context)

@login_required(login_url='login')
def no_authorize(request):
    
    return render(request,'plateform/notauthorize.html')

@login_required(login_url='login')
def make_customer(request,pk,cat):
    user = User.objects.get(id=pk)
    customer_group = Group.objects.get(name='customer')
    user_group= Group.objects.get(name=cat)
    
    
    if cat=='expert':
        Customer.objects.create(
            user=user,firstname=user.username,email=user.email,status='expert'
        )
        
    if cat=='patient':
        Customer.objects.create(
            user=user,firstname=user.username,email=user.email,status='patient'
        )
    
    customer_group.user_set.add(user)
    user_group.user_set.add(user)

    return redirect('dashboard_user')

@login_required(login_url='login')
def update_customer_status(request,pk,cat):

    user = User.objects.get(id=pk)
    user_group= Group.objects.get(name=cat)
    patient_group = Group.objects.get(name='patient')
    expert_group = Group.objects.get(name='expert')
    
    Customer.objects.filter(id=user.customer.id).update(status=cat)

    if cat=='expert':
        patient_group.user_set.remove(user)
        
    if cat=='patient':
        expert_group.user_set.remove(user)
        
    
    user_group.user_set.add(user)

    return redirect('dashboard_user')

@login_required(login_url='login')
def confirm_mail(request,mode):
    context =  {
        'mode':mode
    }
    return render(request,'plateform/mailConfirm.html',context)

@login_required(login_url='login')
def message_ask_mode_admin(request,mode):
    username = request.user.username
    from_email = request.user.email

    subject ="Demand of Access"
    text_content = "Dear admin, "+username+ " want to be "+ mode +", to give him the access, click "
    
    to = ['hadrien.gayaptagheu@esprit.tn','ayoub.mlaouah@esprit.tn']

    send_mail_admin(subject=subject,text_content=text_content,from_email=from_email,to=to)
    

    return redirect('confirm_mail',mode)


def send_mail_admin(subject,text_content,from_email,to=[]):
    subject, from_email, to = subject, from_email, to
    text_content = text_content
    html_content = '<a href="http://127.0.0.1:8000/dashboard_login/">here</a>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(text_content+html_content, "text/html")

    msg.send()


