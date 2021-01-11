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
import datetime
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Sum
from django.db import connection

from magic_admin import Magic
# A util provided by `magic_admin` to parse the auth header value.
from magic_admin.utils.http import parse_authorization_header_value
#from magic_admin.error import DIDTokenError
#from magic_admin.error import RequestError

from .models import Contract, Token, LikeHistory, Profile, Wallet


def index(request):
    '''
    Index page on the API
    '''
    return HttpResponse("Index")



@method_decorator(csrf_exempt, name='dispatch')
def mylikes(request):
    '''
    Get list of my likes
    '''
    try:
        did_token = parse_authorization_header_value(
            request.headers.get('Authorization'),
        ).replace("%3D","=")
    except:
        status_code = 400
        response_body = {
                    "error": {
                        "code": status_code,
                        "message": "Missing authentication token"
                    }
                }
        return JsonResponse(response_body, status=status_code)

    magic = Magic(api_secret_key='pk_test_7FF6C3036AF5DE22')

    # Validate the did_token.
    try:
        magic.Token.validate(did_token)
        public_address = magic.Token.get_public_address(did_token)
    except:
        # Return early with error message. The 401 will trigger a signout on the frontend
        status_code = 401
        response_body = {
                    "error": {
                        "code": status_code,
                        "message": "Invalid or expired authentication token"
                    }
                }
        return JsonResponse(response_body, status=status_code)


    wallet = Wallet.objects.get_or_create(address=public_address)[0]
    if not wallet.profile:
        wallet.profile = Profile.objects.create()
    wallet.last_authenticated = datetime.datetime.now(tz=timezone.utc)
    wallet.save()


    with connection.cursor() as cursor:
        cursor.execute("""
        select c.address, token_identifier, SUM(value) as likes
        from api_profile p
        join api_wallet w
        on w.profile_id = p.id
        join api_likehistory h
        on p.id = h.profile_id
        join api_token t
        on t.id = h.token_id
        join api_contract c
        on c.id = t.contract_id
        where w.address = %s
        group by c.address, token_identifier
        having likes > 0
        """, (public_address, ))
        rows = cursor.fetchall()
        like_list = []
        for row in rows:
            like_list.append({
                "contract": row[0],
                "token_id": row[1]
            })

    #my_wallet_addresses = list(Wallet.objects.filter(profile=wallet.profile).values_list("address"))

    response_body = {
            "data": { 
                "like_list": like_list,
                "my_name": wallet.profile.name,
                "my_img_url": wallet.profile.img_url,
                "my_address": public_address
            }
        }
    return JsonResponse(response_body)







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
        '''

        try:
            did_token = parse_authorization_header_value(
                request.headers.get('Authorization'),
            ).replace("%3D","=")
        except:
            status_code = 401
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Missing authentication token"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        magic = Magic(api_secret_key='pk_test_7FF6C3036AF5DE22')

        # Validate the did_token.
        try:
            magic.Token.validate(did_token)
            public_address = magic.Token.get_public_address(did_token)
        except:
            # Return early with error message. The 401 will trigger a signout on the frontend
            status_code = 401
            response_body = {
                        "error": {
                            "code": status_code,
                            "message": "Invalid or expired authentication token"
                        }
                    }
            return JsonResponse(response_body, status=status_code)

        json_body = json.loads(request.body.decode())
        action = json_body.get('action')
        creator_address = json_body.get('creator_address')
        creator_name = json_body.get('creator_name')
        creator_img_url = json_body.get('creator_img_url')
        

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
        wallet = Wallet.objects.get_or_create(address=public_address)[0]
        if not wallet.profile:
            wallet.profile = Profile.objects.create()
        wallet.last_authenticated = datetime.datetime.now(tz=timezone.utc)
        wallet.save()

        contract = Contract.objects.get_or_create(address=asset_contract_address)[0]
        token = Token.objects.get_or_create(contract=contract, token_identifier=token_id)[0]

        value = 0
        if action=="like":
            value = 1
            if token.creator is None:

                # Attempt to add creator wallet/profile/metadata for leaderboard scoring
                if creator_address:
                    # Get/generate the wallet
                    creator_wallet = Wallet.objects.get_or_create(address=creator_address)[0]
                    if not creator_wallet.profile:
                        # Create new a profile if needed
                        creator_wallet.profile = Profile.objects.create(name=creator_name, img_url=creator_img_url)
                        creator_wallet.save()
                    else:
                        # See if we can augment an existing profile
                        creator_profile = creator_wallet.profile
                        need_to_update = False
                        if creator_profile.name is None and creator_name:
                            creator_profile.name = creator_name
                            need_to_update = True
                        if creator_profile.img_url is None and creator_img_url:
                            creator_profile.img_url = creator_img_url
                            need_to_update = True
                        if need_to_update:
                            creator_profile.save()

                    token.creator = creator_wallet
                    token.save()


        elif action=="unlike":
            value = -1



        # Skip duplicate submissions
        recent_history = LikeHistory.objects.filter(profile=wallet.profile, token=token).order_by('-added').first()
        if recent_history and recent_history.value == value:
            pass
        else:
            LikeHistory.objects.create(profile=wallet.profile, token=token, value=value)


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

        with connection.cursor() as cursor:
            cursor.execute("""
            select c.address, token_identifier, SUM(value) as likes
            from api_profile p
            join api_wallet w
            on w.profile_id = p.id
            join api_likehistory h
            on p.id = h.profile_id
            join api_token t
            on t.id = h.token_id
            join api_contract c
            on c.id = t.contract_id
            group by c.address, token_identifier
            having likes > 0 
            order by likes desc
            limit 8
            
            """)
            rows = cursor.fetchall()
            
            contract_list = []
            token_list = []

            for row in rows:
                contract_list.append(row[0])
                token_list.append(row[1])

        # TBD - create the token list query
        # Query
        url = "https://api.opensea.io/api/v1/assets"
        querystring = {
            "order_direction":"desc",
            "offset":"0",
            "order_by": "sale_price",
            "token_ids": token_list,
            "asset_contract_addresses": contract_list,
            "limit":"50" #Capped at 50
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
            "data": sorted(opensea_json, key = lambda i: i['showtime']['like_count'], reverse=True)
        }
        return JsonResponse(response_body)



class OwnedView(View):
    '''
    Lists the owned art on the profile page
    '''

    def get(self, request):
        '''
        Params: address (optional)
        '''

        address = request.GET.get('address')

        if not address or not bool(re.match(r"0x([0-9a-z]{40})+$", address)):
            try:
                did_token = parse_authorization_header_value(
                    request.headers.get('Authorization'),
                ).replace("%3D","=")
            except:
                
                status_code = 400
                response_body = {
                            "error": {
                                "code": status_code,
                                "message": "Missing address and authentication token"
                            }
                        }
                return JsonResponse(response_body, status=status_code)

            magic = Magic(api_secret_key='pk_test_7FF6C3036AF5DE22')

            # Validate the did_token.
            try:
                magic.Token.validate(did_token)
                address = magic.Token.get_public_address(did_token)
            except:
                # Return early with error message
                status_code = 401
                response_body = {
                            "error": {
                                "code": status_code,
                                "message": "Missing address and expired authentication token"
                            }
                        }
                return JsonResponse(response_body, status=status_code)
        


        wallet = Wallet.objects.filter(address=address).first()
        if wallet and wallet.profile:
            address_list = list(Wallet.objects.filter(profile=wallet.profile).values_list("address"))
        else:
            address_list = [address]

        asset_list = []
        for owner in address_list:
                
            # Query
            url = "https://api.opensea.io/api/v1/assets"
            querystring = {
                "order_direction":"desc",
                "offset":"0",
                "order_by": "sale_price",
                "owner": owner,
                "limit":"50" #Capped at 50
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

                asset_list.append(asset)


        response_body = {
            "data": sorted(asset_list, key = lambda i: i['showtime']['like_count'], reverse=True)
        }
        return JsonResponse(response_body)



class LikedView(View):
    '''
    Lists the liked art on the profile page
    '''

    def get(self, request):
        '''
        Params: address (optional)
        '''

        address = request.GET.get('address')

        if not address or not bool(re.match(r"0x([0-9a-z]{40})+$", address)):
            try:
                did_token = parse_authorization_header_value(
                    request.headers.get('Authorization'),
                ).replace("%3D","=")
            except:
                
                status_code = 400
                response_body = {
                            "error": {
                                "code": status_code,
                                "message": "Missing address and authentication token"
                            }
                        }
                return JsonResponse(response_body, status=status_code)

            magic = Magic(api_secret_key='pk_test_7FF6C3036AF5DE22')

            # Validate the did_token.
            try:
                magic.Token.validate(did_token)
                address = magic.Token.get_public_address(did_token)
            except:
                # Return early with error message
                status_code = 401
                response_body = {
                            "error": {
                                "code": status_code,
                                "message": "Missing address and expired authentication token"
                            }
                        }
                return JsonResponse(response_body, status=status_code)
        


        wallet = Wallet.objects.filter(address=address).first()

        if wallet is None or wallet.profile is None:
            # Return early - there are no likes
            response_body = {
                "data": []
            }
            return JsonResponse(response_body)


        with connection.cursor() as cursor:
            cursor.execute("""
            select c.address, token_identifier, SUM(value) as likes
            from api_profile p
            join api_wallet w
            on w.profile_id = p.id
            join api_likehistory h
            on p.id = h.profile_id
            join api_token t
            on t.id = h.token_id
            join api_contract c
            on c.id = t.contract_id
            where w.address = %s
            group by c.address, token_identifier
            having likes > 0
            """, (address, ))
            rows = cursor.fetchall()
            
            contract_list = []
            token_list = []

            for row in rows:
                contract_list.append(row[0])
                token_list.append(row[1])

        # TBD - create the token list query
        # Query
        url = "https://api.opensea.io/api/v1/assets"
        querystring = {
            "order_direction":"desc",
            "offset":"0",
            "order_by": "sale_price",
            "token_ids": token_list,
            "asset_contract_addresses": contract_list,
            "limit":"50" #Capped at 50
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
            "data": sorted(opensea_json, key = lambda i: i['showtime']['like_count'], reverse=True)
        }
        return JsonResponse(response_body)



class CollectionListView(View):
    '''
    Lists the Collection items on the homepage
    '''

    def get(self, request):
        '''
        Params: none
        '''


        response_body = {
            "data": [
                
                {
                    "name": "SuperRare",
                    "value": "superrare"
                },
                {
                    "name": "Rarible",
                    "value": "rarible"
                },
                {
                    "name": "MakersPlace",
                    "value": "makersplace"
                },
                {
                    "name": "Known Origin",
                    "value": "known-origin"
                }
            ]
        }
        return JsonResponse(response_body)




class CollectionView(View):
    '''
    Lists the Collection items on the homepage
    '''

    def get(self, request):
        '''
        Params: collection (required)
        '''

        collection = request.GET.get('collection')


        if not collection or not bool(re.match(r"([a-z\-])+$", collection)):
            # set default
            collection = "superrare"


        # TBD - create the token list query
        # Query
        url = "https://api.opensea.io/api/v1/assets"
        querystring = {
            "order_direction":"desc",
            "offset":"0",
            "order_by": "sale_price",
            "collection": collection,
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
            "data": sorted(opensea_json, key = lambda i: i['showtime']['like_count'], reverse=True)
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

        top_creators = []
        with connection.cursor() as cursor:
            cursor.execute("""
            select p.id, p.name, p.img_url, min(w.address) as 'address', sum(value) as 'likes', max(h.added) as 'last_like'
            from api_likehistory h
            join api_token t on t.id = h.token_id
            join api_wallet w on w.id = t.creator_id
            join api_profile p on p.id = w.profile_id
            group by p.id, p.name, p.img_url
            having likes > 0 
            order by likes desc, name desc, last_like desc
            
            limit 10
            """)
            rows = cursor.fetchall()
            for row in rows:
                top_creators.append({
                    "profile_id": row[0],
                    "name": row[1],
                    "image_url": row[2],
                    "address": row[3],
                    "like_count": row[4]
                })

        response_body = {
            "data": top_creators
        }
        return JsonResponse(response_body)






class ProfileView(View):
    '''
    Lists the tokens owned for an address
    '''

    def get(self, request):
        '''
        Params: address (optional - in query string)
        '''
        address = request.GET.get('address')

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
        '''


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
                "owned": opensea_json
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
