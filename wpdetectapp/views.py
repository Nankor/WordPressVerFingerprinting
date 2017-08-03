from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import fingerprinting


@csrf_exempt
def detectversion(request):
    if request.method == 'GET':
        return JsonResponse({"domain": "domainName"}, status=201)
    elif request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            if 'domain' not in data:
                raise Exception('Bad Request!')
            fpobj = fingerprinting.FingerPrinting()
            result = fpobj.detect(data['domain'])
            if result is None:
                data['result'] = 'Cannot detect WP version'
            else:
                data['result'] = result
        except Exception as e:
            print e
            dataErr = {'error': str(e)}
            return JsonResponse(dataErr, status=400)
        else:
            return JsonResponse(data, status=201)
