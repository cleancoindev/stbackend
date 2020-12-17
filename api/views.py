'''
*** STATUS CODES ***

200 - OK	                Everything worked as expected.
400 - Bad Request	        The request was unacceptable, often due to missing a required parameter.
401 - Unauthorized	        No valid authorization was provided.
402 - Request Failed	    The parameters were valid but the request failed.
404 - Not Found	            The requested resource doesn't exist.
429 - Too Many Requests	    Too many requests hit the API too quickly.
500 - Server Error	        Something went wrong on our end.

*** RESPONSE STRUCTURE ***

Successful requests will return a "data" object:
{
    "data": {
        "message": "It worked!"
    }
}

Unsuccessful requests will return an "error" object:
{
    "error": {
        "code": 400,
        "message": "Required parameter missing: token"
    }
}
'''

from django.http import HttpResponse, JsonResponse
from django.views import View


def index(request):
    '''
    Index page on the API
    '''
    return HttpResponse("Index")


class ItemView(View):
    '''
    Returns a single item for the detail page
    '''

    def get(self, request):
        '''
        Params: token (required)
        '''
        token = request.GET.get("token")

        if not token:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: token"
                        }
                    }
            return JsonResponse(response_body, status=status_code)
        
        # TBD: Check to see if it's a valid token. 
        # TBD: If not valid, return with error message
        
        response_body = {
                        "data": {
                            "token": token,
                            "name": "Name",
                            "creator": "Creator",
                            "owner": "Owner",
                            "price": "Price"
                        }
                    }
        return JsonResponse(response_body)


class SearchView(View):
    '''
    Testing HTTP methods
    '''

    def get(self, request):
        '''Get method'''
        # <view logic>
        return JsonResponse({'method':'get'})


class FeaturedView(View):
    '''
    Lists the Featured Digital Art on the homepage
    '''

    def get(self, request):
        '''Get method'''
        # <view logic>
        return JsonResponse({'method':'get'})


class LeaderboardView(View):
    '''
    Lists the top creators and art on the homepage
    '''

    def get(self, request):
        '''Get method'''
        # <view logic>
        return JsonResponse({'method':'get'})



class TestView(View):
    '''
    Testing HTTP methods
    '''

    def get(self, request):
        '''Get method'''
        # <view logic>
        return JsonResponse({'method':'get'})

    def post(self, request):
        '''Post method'''
        # <view logic>
        return JsonResponse({'method':'post'})

    def put(self, request):
        '''Put method'''
        # <view logic>
        return JsonResponse({'method':'put'})

    def patch(self, request):
        '''Patch method'''
        # <view logic>
        return JsonResponse({'method':'patch'})

    def delete(self, request):
        '''Delete method'''
        # <view logic>
        return JsonResponse({'method':'delete'})
        