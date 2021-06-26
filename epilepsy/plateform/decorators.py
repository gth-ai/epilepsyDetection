from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request,*args,**kwargs)
    
    return wrapper_func

def allowed_user(allowed_roles= []):
    def decorator(view_func):
        def wrapper_func(request,*args,**kwargs):
            group_list = []

            if request.user.groups.exists():
                for i in range(len(request.user.groups.all())):
                    group_list.append(request.user.groups.all()[i].name)
            
            for i in range(len(group_list)):
                if group_list[i] in allowed_roles :
                    return view_func(request,*args,**kwargs)
            
            else:
                return redirect('no_authorize')
        
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                print(group)

            if group == 'customer':
                return redirect('home')

            if group == 'admin':
                return view_func(request, *args, **kwargs)

            else:
                return redirect('home')

    return wrapper_function