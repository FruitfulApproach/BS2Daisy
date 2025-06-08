def _404(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, '404.html')

def contacts(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'contacts.html')

def faq(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'faq.html')

def features(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'features.html')

def forgotten_password(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'forgotten-password.html')

def index(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'index.html')

def integrations(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'integrations.html')

def login(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'login.html')

def pricing(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'pricing.html')

def signup(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'signup.html')

def testimonials(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'testimonials.html')
