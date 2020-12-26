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
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
#from gql import gql, Client
#from gql.transport.requests import RequestsHTTPTransport
import requests



'''
transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/wighawag/eip721-subgraph',
    verify=True,
    retries=3,
)
subgraph_client = Client(transport=transport)
'''

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

    def get(self, request, address, token_id):

        '''
        Params: token (required)
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
        response = requests.get("https://api.opensea.io/api/v1/asset/{address}/{token_id}".format(address=address, token_id=token_id))

        if response.status_code!=200:
            status_code = response.status_code
            response_body = {
                "error": {
                    "code": status_code,
                    "message": "Error from OpenSea API"
                }
            }
            return JsonResponse(response_body, status=status_code)


        #For now, just return full opensea API
        return JsonResponse(response.json())



        # query = '''query {{

        #         token(id: "{address}_{token_id}") {{
        #             id
        #             contract {{
        #                 id
        #             }}
        #             tokenID
        #             owner {{
        #                 id
        #             }}
        #             tokenURI
        #         }}
        #     }}
        # '''.format(address=address, token_id=token_id)

        # token_data = subgraph_client.execute(gql(query))

        # if not token_data['token']:
        #     # Return early with error message
        #     status_code = 404
        #     response_body = {
        #                 "error": {
        #                     "code": status_code,
        #                     "message": "Token not found"
        #                 }
        #             }
        #     return JsonResponse(response_body, status=status_code)


        # #print(token_data)

        # # Check if missing token URI
        # token_uri = token_data['token'].get('tokenURI')

        # if not token_uri:
        #     # Return early with error message
        #     status_code = 402
        #     response_body = {
        #                 "error": {
        #                     "code": status_code,
        #                     "message": "Token does not contain URI"
        #                 }
        #             }
        #     return JsonResponse(response_body, status=status_code)

        # # Check if URI not json
        # if len(token_uri)<22 or token_uri[:22] != "data:application/json,":
        #     # Return early with error message
        #     status_code = 402
        #     response_body = {
        #                 "error": {
        #                     "code": status_code,
        #                     "message": "Token URI does not contain json"
        #                 }
        #             }
        #     return JsonResponse(response_body, status=status_code)


        # token_uri_json = json.loads(token_uri.replace("data:application/json,",""))
        # #print(token_uri_json)

        # name = token_uri_json.get("name")
        # if name:
        #     name = urllib.parse.unquote(name)
        # description = token_uri_json.get("description")
        # if description:
        #     description = urllib.parse.unquote(description)
        # image = token_uri_json.get("image")

        # owner_id = None
        # owner = token_data['token'].get("owner")
        # if owner:
        #     owner_id = owner.get("id")

        # contract_id = None
        # contract = token_data['token'].get('contract')
        # if contract:
        #     contract_id = contract.get("id")

        # response_body = {
        #                 "data": {
        #                     #"id": contract_token_id,
        #                     "contract_id": contract_id,
        #                     "token_id": token_data['token'].get('tokenID'),
        #                     "owner_id": owner_id,
        #                     "name": name,
        #                     "description": description,
        #                     "image": image,
        #                     #"creator": "Creator",
        #                     #"price": "Price",
        #                 }
        #             }
        # return JsonResponse(response_body)



    def post(self, request, address, token_id):
        '''
        Params:
        1. address (required - in path)
        2. token_id (required - in path)
        3. action (required - in body) - values include "like" & "unlike"
        4. user_id (required - in body)
        '''

        json_body = json.loads(request.body.decode())
        action = json_body.get('action')
        user_id = json_body.get('user_id')

        #action = request.POST.get("action") # this is the syntax for forms

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

        items_list = [
            {
                "token": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                "name": "Name",
                "creator": "Creator",
                "owner": "Owner",
                "price": "Price",
                "thumbnail_url": "",
                "like_count": 232
            },
            {
                "token": "token2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32
            },
            {
                "token": "token2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32
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
                    "token": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
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
                    "token": "token2",
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
                    "token": "token3",
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
                "token": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                "name": "Name",
                "creator": "Creator",
                "owner": "Owner",
                "price": "Price",
                "thumbnail_url": "",
                "like_count": 232,
                "sharable_link": ""
            },
            {
                "token": "token2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32,
                "sharable_link": ""
            },
            {
                "token": "token3",
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
                "token": "0x752aa32a2cc49aed842874326379ea1f95b1cbe6",
                "name": "Name",
                "creator": "Creator",
                "owner": "Owner",
                "price": "Price",
                "thumbnail_url": "",
                "like_count": 232,
                "sharable_link": ""
            },
            {
                "token": "token2",
                "name": "Name 2",
                "creator": "Creator 2",
                "owner": "Owner 2",
                "price": "Price 2",
                "thumbnail_url": "",
                "like_count": 32,
                "sharable_link": ""
            },
            {
                "token": "token3",
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
