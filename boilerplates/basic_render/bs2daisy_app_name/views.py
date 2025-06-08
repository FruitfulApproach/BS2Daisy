from django.shortcuts import render


# BS2Daisy: push ignore
def basic_render(request):              # BS2Daisy: merge (the default)
    return render(request, 'bs2daisy_template_name.html')

   

# BS2Daisy: pop ignore