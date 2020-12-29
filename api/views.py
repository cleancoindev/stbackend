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
import re
import requests
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Sum
from .models import MagicUser, Contract, Token, LikeHistory, Profile


def index(request):
    '''
    Index page on the API
    '''
    return HttpResponse("Index")


@method_decorator(csrf_exempt, name='dispatch')
class TokenView(View):
    '''
    Returns a single item for the detail page
    '''

    def get(self, request, asset_contract_address, token_id):

        '''
        Params: token (required)
        '''

        if not asset_contract_address:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: asset_contract_address"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        if not token_id:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: token_id"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        # Check to see if it's a valid address format
        # example: "0x0000000000001b84b1cb32787b0d64758d019317"

        if not bool(re.match(r"0x([0-9a-z]{40})+$", asset_contract_address)):
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "asset_contract_address not in expected format"
                        }
                    }
            return JsonResponse(response_body, status=status_code)



        # Continue with query
        response = requests.get("https://api.opensea.io/api/v1/asset/{asset_contract_address}/{token_id}".format(asset_contract_address=asset_contract_address, token_id=token_id))

        if response.status_code!=200:
            status_code = response.status_code
            response_body = {
                "error": {
                    "code": status_code,
                    "message": "Error from OpenSea API"
                }
            }
            return JsonResponse(response_body, status=status_code)

        opensea_json = response.json()

        # Add the "showtime" data to the original response
        like_count = list(LikeHistory.objects.filter(
            token__token_identifier=token_id,
            token__contract__address=asset_contract_address
        ).aggregate(Sum('value')).values())[0] or 0

        opensea_json['showtime'] = {
            "like_count": like_count
        }

        #For now, just return full opensea API response
        response_body = {
            "data": opensea_json
        }
        return JsonResponse(response_body)


    def post(self, request, asset_contract_address, token_id):
        '''
        Params:
        1. address (required - in path)
        2. token_id (required - in path)
        3. action (required - in body) - values include "like" & "unlike"
        4. user_email (required - in body)
        '''

        json_body = json.loads(request.body.decode())
        action = json_body.get('action')
        user_email = json_body.get('user_email')

        if not asset_contract_address:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: asset_contract_address"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        if not token_id:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: token_id"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        # Check to see if it's a valid address format
        # example: "0x0000000000001b84b1cb32787b0d64758d019317"

        if not bool(re.match(r"0x([0-9a-z]{40})+$", asset_contract_address)):
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "asset_contract_address not in expected format"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        if not user_email or user_email.strip()=="":
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: user_email"
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
        magic_user = MagicUser.objects.get_or_create(email=user_email)[0]
        contract = Contract.objects.get_or_create(address=asset_contract_address)[0]
        token = Token.objects.get_or_create(contract=contract, token_identifier=token_id)[0]

        value = 0
        if action=="like":
            value = 1
        elif action=="unlike":
            value = -1

        # Skip duplicate submissions
        recent_history = LikeHistory.objects.filter(magic_user=magic_user, token=token).order_by('-added').first()
        if recent_history and recent_history.value == value:
            pass
        else:
            LikeHistory.objects.create(magic_user=magic_user, token=token, value=value)

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
                "token": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                "name": "Name",
                "creator": "Creator",
                "owner": "Owner",
                "price": "Price",
                "thumbnail_url": "",
                "history": []
            },
            {
                "token": "token2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
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


        # Query
        url = "https://api.opensea.io/api/v1/assets"
        querystring = {
            "order_direction":"asc",
            "offset":"0",
            "limit":"20" #Capped at 50
        }
        response = requests.request("GET", url, params=querystring)

        if response.status_code!=200:
            status_code = response.status_code
            response_body = {
                "error": {
                    "code": status_code,
                    "message": "Error from OpenSea API"
                }
            }
            return JsonResponse(response_body, status=status_code)


        opensea_json = response.json().get('assets')

        for asset in opensea_json:

            # Add the "showtime" data to the original response
            if asset.get('token_id') and asset.get('asset_contract') and asset['asset_contract'].get('address'):
                like_count = list(LikeHistory.objects.filter(
                    token__token_identifier=asset['token_id'],
                    token__contract__address=asset['asset_contract']['address']
                ).aggregate(Sum('value')).values())[0] or 0
            else:
                like_count = 0

            asset['showtime'] = {
                "like_count": like_count
            }

        response_body = {
            "data": opensea_json
        }
        return JsonResponse(response_body)


class LeaderboardView(View):
    '''
    Lists the top creators and art on the homepage
    '''

    def get(self, request):
        '''
        Params: none
        '''


        # Query
        url = "https://api.opensea.io/api/v1/assets"
        querystring = {
            "order_direction":"desc",
            "offset":"0",
            "limit":"20" #Capped at 50
        }
        response = requests.request("GET", url, params=querystring)

        if response.status_code!=200:
            status_code = response.status_code
            response_body = {
                "error": {
                    "code": status_code,
                    "message": "Error from OpenSea API"
                }
            }
            return JsonResponse(response_body, status=status_code)


        opensea_json = response.json().get('assets')

        for asset in opensea_json:

            # Add the "showtime" data to the original response
            if asset.get('token_id') and asset.get('asset_contract') and asset['asset_contract'].get('address'):
                like_count = list(LikeHistory.objects.filter(
                    token__token_identifier=asset['token_id'],
                    token__contract__address=asset['asset_contract']['address']
                ).aggregate(Sum('value')).values())[0] or 0
            else:
                like_count = 0

            asset['showtime'] = {
                "like_count": like_count
            }

        response_body = {
            "data": opensea_json
        }
        return JsonResponse(response_body)






class ProfileView(View):
    '''
    Lists the tokens owned for an address
    '''

    def get(self, request, address):
        '''
        Params: address (required - in path)
        '''

        if not address:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: address"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        # Check to see if it's a valid address format
        # example: "0x0000000000001b84b1cb32787b0d64758d019317"

        if not bool(re.match(r"0x([0-9a-z]{40})+$", address)):
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "address not in expected format"
                        }
                    }
            return JsonResponse(response_body, status=status_code)



        # Continue with query
        url = "https://api.opensea.io/api/v1/assets"
        querystring = {
            "owner":address,
            "order_direction":"desc",
            "offset":"0",
            "limit":"20" #Capped at 50
        }
        response = requests.request("GET", url, params=querystring)

        if response.status_code!=200:
            status_code = response.status_code
            response_body = {
                "error": {
                    "code": status_code,
                    "message": "Error from OpenSea API"
                }
            }
            return JsonResponse(response_body, status=status_code)


        opensea_json = response.json().get('assets')

        for asset in opensea_json:

            # Add the "showtime" data to the original response
            if asset.get('token_id') and asset.get('asset_contract') and asset['asset_contract'].get('address'):
                like_count = list(LikeHistory.objects.filter(
                    token__token_identifier=asset['token_id'],
                    token__contract__address=asset['asset_contract']['address']
                ).aggregate(Sum('value')).values())[0] or 0
            else:
                like_count = 0

            asset['showtime'] = {
                "like_count": like_count
            }

        response_body = {
            "data": {
                "profile_address": address,
                "tokens_owned": opensea_json
            }
        }
        return JsonResponse(response_body)


class ContractView(View):
    '''
    Lists the tokens created by a contract
    '''

    def get(self, request, address):
        '''
        Params: address (required - in path)
        '''

        if not address:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: address"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        # Check to see if it's a valid address format
        # example: "0xfa2c6c8599026583dbc274484e5a088880c8de8e"

        if not bool(re.match(r"0x([0-9a-z]{40})+$", address)):
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "address not in expected format"
                        }
                    }
            return JsonResponse(response_body, status=status_code)



        # Continue with query
        url = "https://api.opensea.io/api/v1/assets"
        querystring = {
            "asset_contract_address":address,
            "order_direction":"desc",
            "offset":"0",
            "limit":"20" #Capped at 50
        }
        response = requests.request("GET", url, params=querystring)

        if response.status_code!=200:
            status_code = response.status_code
            response_body = {
                "error": {
                    "code": status_code,
                    "message": "Error from OpenSea API"
                }
            }
            return JsonResponse(response_body, status=status_code)

        opensea_json = response.json().get('assets')

        for asset in opensea_json:

            # Add the "showtime" data to the original response
            if asset.get('token_id') and asset.get('asset_contract') and asset['asset_contract'].get('address'):
                like_count = list(LikeHistory.objects.filter(
                    token__token_identifier=asset['token_id'],
                    token__contract__address=asset['asset_contract']['address']
                ).aggregate(Sum('value')).values())[0] or 0
            else:
                like_count = 0

            asset['showtime'] = {
                "like_count": like_count
            }


        response_body = {
            "data": {
                "contract_address": address,
                "tokens_created": opensea_json
            }
        }
        return JsonResponse(response_body)

@method_decorator(csrf_exempt, name='dispatch')
class UserAddView(View):
    '''
    Endpoint for scraper to add user data
    '''

    def post(self, request):
        '''
        Params:
        1. address (required - in json body)
        2. name (optional - in json body)
        3. twitter (optional - in json body)
        '''

        json_body = json.loads(request.body.decode())
        address = json_body.get('address')
        if address and address.strip()=="":
            address = None

        name = json_body.get('name')
        if name and name.strip()=="":
            name = None

        twitter = json_body.get('twitter')
        if twitter and twitter.strip()=="":
            twitter = None

        if not address:
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Required parameter missing: address"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        # Check to see if it's a valid address format
        # example: "0x0000000000001b84b1cb32787b0d64758d019317"

        if not bool(re.match(r"0x([0-9a-z]{40})+$", address)):
            # Return early with error message
            status_code = 400
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "address not in expected format"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        profile = Profile.objects.get_or_create(address=address)[0]
        profile.name = name
        profile.twitter = twitter
        profile.save()

        # Return empty 200
        return HttpResponse("")
