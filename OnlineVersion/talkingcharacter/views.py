
from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from .models import ServerStatus
from django.utils.decorators import method_decorator
from django.views import View
import json
from .utils import video, get_chatgpt_response, Newest_link, update_video_link_and_set_done, create_video
import logging
from .models import VideoLink
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

status_text = "standard"
logging.basicConfig(filename='updateview.log', level=logging.INFO)
logger = logging.getLogger(__name__)
video_id = ""

#def startconversation(request)
@method_decorator(csrf_exempt, name='dispatch')
class ProcessTranscriptView(View):

    
    def post(self, request):
        global status_text, Newest_link, new_status, transcript, video_id
        saverequest = request
        data = json.loads(request.body)
        transcript = data.get('transcript', '')
        gptResponse = get_chatgpt_response(transcript)
        try:
            x = video.request_video(gptResponse, self)
            print(x)   
        except Exception as E:
            print(E)
            return JsonResponse({"message": "something with the video request went wrong"})
        status_text = "The video has actually been requested"
        print(status_text)

        new_status = "The video has actually been requested"
        video_id = create_video('http://meinlink.com/video')

        # For demonstration purposes, we'll just echo it back
        
        return JsonResponse({"message": "Script received successfully!"})

def get_latest_video_link(request):
    # Das neueste Videoobjekt holen
    latest_video = VideoLink.objects.all().order_by('-id').first()

    if latest_video and latest_video.status == 'DONE':
        # Wenn das neueste Video den Status 'DONE' hat, verwenden Sie dessen Link
        latest_video_link = latest_video.video_link
        context = {'video_link': latest_video_link}
        logger.info(f"Gegebener Context zum Neu-Rendern: {context}")
        return render(request, "index.html", context)
    else:
        # Wenn das neueste Video nicht den Status 'DONE' hat, geben Sie eine JsonResponse zurück
        return JsonResponse({"error": "Das neueste Video ist noch nicht fertig."})

class CharacterView(TemplateView):
    template_name = "index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        global Newest_link
        context['video_link'] = Newest_link  # Verwenden des gespeicherten Links
        return context
   
    @staticmethod
    def updateview(request):
        global Newest_link

        
        # Loggen, dass die Methode aufgerufen wurde
        logger.info("updateview Methode aufgerufen")

        # Beispiel: Loggen des Link-Wertes
        logger.info(f"Erhaltener Link bei  updateview: {Newest_link}")
        #funtion that ONLY updates the video
        link = Newest_link

        
               
        context = {'video_link': link}
        #return JsonResponse(context)
        return render(request=request, template_name="index.html", context=context)
        






def get_server_status(request):
    # Your logic to determine server status. For demonstration:
    global status_text

    return JsonResponse({"status": status_text})


@require_POST
def update_server_status(request):
    new_status = request.POST.get('status_text')
    if new_status:
        ServerStatus.objects.create(status_text=new_status)
        return JsonResponse({"message": "Status updated successfully!"})
    else:
        return JsonResponse({"error": "Status text not provided!"}, status=400)
 
    
@method_decorator(csrf_exempt, name='dispatch')
@require_http_methods(["GET", "POST"])
def WebhookReceiver(request):
        global video_id
#I still have to check if D-ID acutally sends a post- and not a get request 
        logging.basicConfig(filename='webhook.log', level=logging.INFO)
        logging.info('Webhook Response: %s', {'status': 'webhook worked'})
        print(request)
        payload = request.body

        link = video.get_video(payload)
        update_video_link_and_set_done(video_id, link)
        """
        # Senden der neuen Video-URL an alle verbundenen Websocket-Clients
        channel_layer = get_channel_layer()
        group_name = 'group_name'  # Name der Gruppe, der alle Websocket-Clients zugeordnet sind
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_video_url',
                'video_url': link
            }
        )      
        """
        
        return JsonResponse({'status':'webhook worked', 'video_link': link}, safe=False)
    


    



    