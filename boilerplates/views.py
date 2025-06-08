
def simply_render(request):
    from django.shortcuts import render       ## BS2Daisy: keep local
    
    return render(request, 'template_name.html')

   
