def login_view(request):
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
            return render(request, {template_path}, {{'form': form, 'error': 'Invalid username or password'}})
      else:
         return render(request, {template_path}, {{'form': form, 'error': 'Invalid username or password'}})
   else:
      form = AuthenticationForm()
   return render(request, {template_path}, {{'form': form}})

def zempty(request):
   pass