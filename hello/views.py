# hello/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
import logging
import openai

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'hello/home.html')

def about(request):
    return render(request, 'hello/about.html', {'title': 'About Us'})

def services(request):
    return render(request, 'services.html', {'title': 'Our Services'})

def contact(request):
    return render(request, 'contact.html', {'title': 'Contact Us'})

def get_poem(request):
    if request.method == 'GET':
        topic = request.GET.get('topic',"Artifical intellegence and programing using python")
        description = request.GET.get('description',"use cases of ai in healthcare ")
          # Print the values for debugging
        logger.debug("Topic: " + topic)
        logger.debug("Description: " + description)

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": topic},
                    {"role": "user", "content": description }
                ]
            )
            poem = completion.choices[0].message['content']
            return JsonResponse({'poem': poem})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)
    

def submit_form(request):
    if request.method == 'POST':
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
                ]
            )
            poem = response['choices'][0]['message']['content']
            return JsonResponse({'poem': poem})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)