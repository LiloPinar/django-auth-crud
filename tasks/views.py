from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, "home.html")

def signup(request):
    if request.method == "GET":
        return render(request, "signup.html", {"form": UserCreationForm})
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password1"],
                )
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(
                    request,
                    "signup.html",
                    {"form": UserCreationForm, "error": "Username already exists"},
                )
        return render(
            request,
            "signup.html",
            {"form": UserCreationForm, "error": "Password do not match"},
        )

@login_required
def tasks(request):
    # Mostrar solo las tareas pendientes que no son importantes
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True, important=False)
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks_completed.html', {'tasks': tasks})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.datecompleted = timezone.now()  # Marca la tarea como completada
    task.save()
    return redirect('tasks_completed')  # Redirige a Tareas Completadas


@login_required
def important_tasks(request):
    tasks = Task.objects.filter(important=True, datecompleted__isnull=True, user=request.user)
    return render(request, 'important_tasks.html', {'tasks': tasks})



@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, "create_task.html", {'form': TaskForm()})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            # Si es importante, redirige a tareas importantes
            if new_task.important:
                return redirect('important_tasks')
            else:
                return redirect('tasks')  # Si no es importante, redirige a tareas pendientes
        except ValueError:
            return render(request, "create_task.html", {
                'form': TaskForm(),
                'error': 'Ingrese tipos de datos correctos'
            })



@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        #print('Visitaron por URL')
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request,'task_detail.html',{
            'task':task,
            'form': form
        })
    else:
        try:
            #print(request.POST)
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request,'task_detail.html',{
            'task':task,
            'form': form,
            'error':'Error updating tasks'
        })



@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
@login_required
def mark_as_important(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.important = not task.important  # Alternar el valor de importante
    task.save()
    return redirect('important_tasks') if task.important else redirect('tasks')


@login_required    
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', 
                  {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'],
                      password=request.POST['password'])
        if user is None:
              return render(request, 'signin.html', {
                  'form': AuthenticationForm,
                  'error':'Username or password is incorrect'
                  })
        else:
            login(request, user)
            return redirect('tasks')
    
