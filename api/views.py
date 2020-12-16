'''
Contains the view logic
'''
from django.http import HttpResponse, JsonResponse
from django.views import View


def index(request):
    '''
    Index page on the API
    '''
    return HttpResponse("Index")


class TestView(View):
    '''
    Testing HTTP methods
    '''

    def get(self, request):
        # <view logic>
        return JsonResponse({'method':'get'})

    def post(self, request):
        # <view logic>
        return JsonResponse({'method':'post'})

    def put(self, request):
        # <view logic>
        return JsonResponse({'method':'put'})

    def patch(self, request):
        # <view logic>
        return JsonResponse({'method':'patch'})

    def delete(self, request):
        # <view logic>
        return JsonResponse({'method':'delete'})
        