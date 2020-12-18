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
        "message": "Required parameter missing: address"
    }
}
'''

import json
import urllib.parse
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def index(request):
    '''
    Index page on the API
    '''
    return HttpResponse("Index")


@method_decorator(csrf_exempt, name='dispatch')
class ItemView(View):
    '''
    Returns a single item for the detail page
    '''

    def get(self, request, token):
        '''
        Params: token (required)
        '''

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
                            "price": "Price",
                            "thumbnail_url": "",
                            "sharable_link": ""
                        }
                    }
        return JsonResponse(response_body)

    def post(self, request, token):
        '''
        Params:
        1. token (required - in path)
        2. action (required - in body) - values include "like" & "unlike"
        3. user_id (required - in body)
        '''

        json_body = json.loads(request.body.decode())
        action = json_body.get('action')
        user_id = json_body.get('user_id')

        #action = request.POST.get("action") # this is the syntax for forms

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

        # TBD: Check to make sure it's a valid token. Return error if not.

        if not user_id:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: user_id"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        # TBD: Check to make sure it's a valid user. Return error if not.

        if not action:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: action"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        if not action in ["like", "unlike"]:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Invalid value for parameter: action"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        # TBD: Process the Like/Unlike

        # Return empty 200
        return HttpResponse("")


class SearchView(View):
    '''
    Returns list of items based on search query
    '''

    def get(self, request):
        '''
        Params: q (required - in query string)
        '''

        query = request.GET.get('q')
        if not query or query.strip()=="":
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing or blank: query"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        unquoted_query = urllib.parse.unquote(query)

        # TBD: perform the search

        items_list = [
            {
                "address": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                "name": "Name",
                "creator": "Creator",
                "owner": "Owner",
                "price": "Price",
                "thumbnail_url": "",
                "sharable_link": "",
                "history": []
            },
            {
                "address": "address2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "sharable_link": "",
                "history": []
            }
        ]

        # Could add in results_count, pages, etc. under data
        response_body = {
                        "data": {
                            "query": unquoted_query,
                            "results": items_list
                        }
                    }
        return JsonResponse(response_body)


class FeaturedView(View):
    '''
    Lists the Featured Digital Art on the homepage
    '''

    def get(self, request):
        '''
        Params: none
        '''

        items_list = [
            {
                "address": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                "name": "Name",
                "creator": "Creator",
                "owner": "Owner",
                "price": "Price",
                "thumbnail_url": "",
                "like_count": 232,
                "sharable_link": ""
            },
            {
                "address": "address2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32,
                "sharable_link": ""
            },
            {
                "address": "address2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32,
                "sharable_link": ""
            }
        ]
        response_body = { "data": items_list }
        return JsonResponse(response_body)


class LeaderboardView(View):
    '''
    Lists the top creators and art on the homepage
    '''

    def get(self, request):
        '''
        Params: none
        '''

        leaderboard_list = [
            {
                "rank": 1,
                "creator": {
                    "name": "Beeple",
                    "thumbnail_url": ""
                },
                "item": {
                    "address": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                    "name": "Name",
                    "thumbnail_url": "",
                    "like_count": 3521
                }
            },
            {
                "rank": 2,
                "creator": {
                    "name": "Fewocious",
                    "thumbnail_url": ""
                },
                "item": {
                    "address": "ADDRESS2",
                    "name": "Name",
                    "thumbnail_url": "",
                    "like_count": 2283
                }
            },
            {
                "rank": 3,
                "creator": {
                    "name": "3LAU",
                    "thumbnail_url": ""
                },
                "item": {
                    "address": "address3",
                    "name": "Name",
                    "thumbnail_url": "",
                    "like_count": 1902
                }
            }
        ]
        response_body = { "data": leaderboard_list }
        return JsonResponse(response_body)


class ProfileView(View):
    '''
    Lists the Art owned for a username or crypto address
    '''

    def get(self, request, username_or_address):
        '''
        Params: username_or_address (required - in path)
        '''

        owned_list = [
            {
                "address": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                "name": "Name",
                "creator": "Creator",
                "owner": "Owner",
                "price": "Price",
                "thumbnail_url": "",
                "like_count": 232,
                "sharable_link": ""
            },
            {
                "address": "address2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32,
                "sharable_link": ""
            },
            {
                "address": "address3",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32,
                "sharable_link": ""
            }
        ]

        liked_list = [
            {
                "address": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                "name": "Name",
                "creator": "Creator",
                "owner": "Owner",
                "price": "Price",
                "thumbnail_url": "",
                "like_count": 232,
                "sharable_link": ""
            },
            {
                "address": "address2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32,
                "sharable_link": ""
            },
            {
                "address": "address3",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32,
                "sharable_link": ""
            }
        ]
        response_body = {
            "data": {
                "display_name": username_or_address,
                "owned": owned_list,
                "liked": liked_list
            }
        }
        return JsonResponse(response_body)
