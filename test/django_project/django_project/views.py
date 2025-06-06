
def contacts(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "contacts.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "contacts.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "contacts.html", {'form': form})

def faq(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "faq.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "faq.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "faq.html", {'form': form})

def features(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "features.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "features.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "features.html", {'form': form})

def forgotten_password(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "forgotten-password.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "forgotten-password.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "forgotten-password.html", {'form': form})

def index(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "index.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "index.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "index.html", {'form': form})

def integrations(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "integrations.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "integrations.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "integrations.html", {'form': form})

def login(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "login.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "login.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "login.html", {'form': form})

def pricing(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "pricing.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "pricing.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "pricing.html", {'form': form})

def signup(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "signup.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "signup.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "signup.html", {'form': form})

def testimonials(request):
   from django.shortcuts import render, redirect
   from django.contrib.auth import authenticate, login
   from django.contrib.auth.forms import AuthenticationForm
   
   if request.method == 'POST':
      form = AuthenticationForm(request, data=request.POST)
      if form.is_valid():
         username = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
         else:
            return render(request, "testimonials.html", {'form': form, 'error': 'Invalid username or password'})
      else:
         return render(request, "testimonials.html", {'form': form, 'error': 'Invalid username or password'})
   else:
      form = AuthenticationForm()
   return render(request, "testimonials.html", {'form': form})
