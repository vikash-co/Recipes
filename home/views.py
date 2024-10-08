from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, login
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from django.contrib.auth.hashers import check_password

# Initialize MongoDB connection
client = MongoClient('mongodb+srv://vs292382:UTbdYfHuXvcXd8E8@cluster0.4g3gt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['recipes']
users_collection = db['auth_user'] 

@login_required(login_url="/login")
def recipes(request):
    if request.method == 'POST':
        data = request.POST
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')
        recipe_image = request.FILES['recipe_image']

        recipe_info = Recipe(recipe_name = recipe_name, recipe_description = recipe_description, recipe_image = recipe_image)
        recipe_info.save()
        return redirect('/')
    queryset = Recipe.objects.all()

    if request.GET.get('search'):
        queryset = queryset.filter(recipe_name__icontains = request.GET.get('search'))
        
        

    context = {'recipes' : queryset}    
    return render(request, "recipe.html", context)

@login_required(login_url="/login")
def delete_recipe(request, id):
    queryset = Recipe.objects.get(id = id)
    queryset.delete()
    return redirect('/')


@login_required(login_url="/login")
def update_recipe(request, id):
    queryset = Recipe.objects.get(id = id)

    if request.method == 'POST':
        data = request.POST
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')
        recipe_image = request.FILES['recipe_image']

        queryset.recipe_name = recipe_name
        queryset.recipe_description = recipe_description
        if recipe_image:       
          queryset.recipe_image = recipe_image
        queryset.save()
        return redirect('/')
    context = {'recipe' : queryset}    
    return render(request, "update_recipe.html", context)


#login
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username') 
        password = request.POST.get('password')
        user = users_collection.find_one({"username": username})

        if not user:
            messages.error(request, 'Invalid Username')
            return redirect('/login')
        
        # Check the password
        if not check_password(password, user['password']):
            messages.error(request, 'Invalid Password')
            return redirect('/login')

        # Log in the user manually
        user_obj = User.objects.get(username=username)
        login(request, user_obj)
        return redirect('/')

        if not User.objects.filter(username = username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login')
        
        user = authenticate(username = username, password = password)

        if user is None:
            messages.error(request, 'Invalid Password')
            return redirect('/login')
        else:
            login(request, user)
            return redirect('/')

   

    return render(request, 'login.html')

def logout_page(request):
    logout(request)
    return redirect('/login')


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name') 
        username = request.POST.get('username') 
        password = request.POST.get('password')

        user = User.objects.filter(username = username)
         
        if user.exists():
            messages.info(request, 'Username already taken')
            return redirect('/register')

        user = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            username = username
        )
        user.set_password(password)
        user.save()

        messages.info(request, 'Account create successfully')

        login(request, user)
        return redirect('/')
    return render(request, 'register.html')