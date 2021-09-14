from django.forms.utils import to_current_timezone
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .models import Todo
from .forms import TodoForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.
def signUpUser(request):

    if request.method == 'GET':
        return render(request,'todo/signup.html',{'form':UserCreationForm()})
    else:
        #Create a new User
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('current')

            except IntegrityError:
                return render(request,'todo/signup.html',{'form':UserCreationForm(),'error':"this user already been taken!"})
        else:
            return render(request,'todo/signup.html',{'form':UserCreationForm(),'error':"password did not matched!"})

@login_required
def current(request):
    todos = Todo.objects.filter(user = request.user,date_completed__isnull=True)
    return render(request,'todo/current.html',{'todos':todos})

@login_required
def logOutUser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')


def home(request):
    return render(request,'todo/home.html')


def logInUser(request):
    if request.method == 'GET':
        return render(request,'todo/login.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is not None:
            login(request,user)
            return redirect('current')
        else:
            return render(request,'todo/login.html',{'form':AuthenticationForm(),'error':"username and/or password is incorrect"})
@login_required
def createTodo(request):
    if request.method == 'GET':
        return render(request,'todo/createTodo.html',{'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newTodo = form.save(commit=False)
            newTodo.user = request.user
            newTodo.save()
            return redirect('current')
        except ValueError:
            return render(request,'todo/createTodo.html',{'form':TodoForm(),'error':"bad data entries, try again"})

@login_required
def viewtodo(request,todo_pk):

    todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)

    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request,'todo/viewtodo.html',{'todo':todo,'form':form})
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('current')
        except ValueError:
            return render(request,'todo/createTodo.html',{'form':TodoForm(),'error':"bad data entries, try again"})


@login_required
def completetodo(request,todo_pk):

    todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)

    if request.method == "POST":

        todo.date_completed = timezone.now()
        todo.save()
        return redirect('current')

@login_required
def deletedtodo(request,todo_pk):

    todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)

    if request.method == "POST":
        todo.delete()
        return redirect('current')
        
@login_required
def completedtodo(request):

    todos = Todo.objects.filter(user = request.user,date_completed__isnull=False).order_by("-date_completed")
    return render(request,'todo/completed.html',{'todos':todos})

