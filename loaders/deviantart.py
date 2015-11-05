from pprint import pprint
import requests
import requests.auth
from uuid import uuid4
from urllib.parse import urlencode

class DeviantArtApiError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code



class DeviantArt(object):
    def __init__(self, authorizationRedirectUri, token):
        self.clientId     = '3823'
        self.clientSecret = 'ebdbe992445cd52b086030439f710fb3'
        self.authorizationRedirectUri = authorizationRedirectUri
        self.token = token


    def getAuthorizationUrl(self):
        params = {
            'response_type' : 'code',
            'client_id'     : self.clientId,
            'redirect_uri'  : self.authorizationRedirectUri,
            'scope'         : 'feed',
            'state'         : str(uuid4()),
        }
        return "https://www.deviantart.com/oauth2/authorize?" + urlencode(params)


    def handleAuthorizationCallback(self, request):
        error = request.args.get('error', '')
        if error:
            return "Error: " + error
        code = request.args.get('code')
        self.getToken(code)


    def getToken(self, code):
        client_auth = requests.auth.HTTPBasicAuth(self.clientId, self.clientSecret)
        post_data = {"grant_type": "authorization_code",
                     "code": code,
                     "redirect_uri": self.authorizationRedirectUri}
        response = requests.post("https://www.deviantart.com/oauth2/token",
                                 auth=client_auth,
                                 data=post_data)
        token_json = response.json()
        token = token_json["access_token"]
        print('DEVIANTART API TOKEN:')
        print(token)

        self.token = token


    def getWorks(self):
        print('POW')
        response = requests.get('https://www.deviantart.com/api/v1/oauth2/feed/home?' + urlencode({'access_token' : self.token}))
        if response.status_code != 200:
            print('ERROR')
            print(response.status_code)
            raise DeviantArtApiError(response.json(), status_code=response.status_code)

        return self.parseFeed(response.json())


    def parseFeed(self, responseDict):
        chunks = [(deviation, item['ts']) for item in responseDict['items'] if item['type'] == 'deviation_submitted' for deviation in item['deviations']]

        imageList = []
        for deviation, timestamp in chunks:
            imageData = {
                'identifier'      : '',
                'authorName'      : '',
                'authorHandle'    : '',
                'authorAvatarUrl' : '',
                'profileUrl'      : '',
                'website'         : '',
                'imageTitle'      : '',
                'imageUrls'       : [],
                'imageTimestamp'  : '',
                'imageType'       : '',
                'nsfw'            : False,
                'width'           : '500',
                'height'          : '500',
                'success'         : False,
                'error'           : 'Unknown error',
            }

            userInfo  = deviation.get('author') or {}
            imageInfo = deviation.get('content') or {}
            imageData['identifier']      = deviation.get('deviationid'),
            imageData['authorName']      = str(userInfo.get('username'))
            imageData['authorHandle']    = str(userInfo.get('username'))
            imageData['authorAvatarUrl'] = str(userInfo.get('usericon'))
            imageData['profileUrl']      = 'http://' + str(userInfo.get('username')) + '.deviantart.com'
            imageData['website']         = 'DeviantArt'
            imageData['imageTitle']      = str(deviation.get('title'))
            imageData['imageUrls']       = [str(imageInfo.get('src'))]
            imageData['imageTimestamp']  = str(timestamp)
            imageData['imageType']       = '"deviation"'
            imageData['nsfw']            = str(deviation.get('is_mature'))
            imageData['width']           = str(imageInfo.get('width')) or '500'
            imageData['height']          = str(imageInfo.get('height')) or '500'
            imageData['success']         = 'True'
            imageData['error']           = ''

            imageList.append(imageData)

        for d in imageList:
            d['identifier'] = d['identifier'][0] #??????????????????????
        return imageList






lold = {
    'cursor': 'MD0wJjE9OCYyPTImMz0wJjQ9MCY1PTAmNj0wJjc9MCY4PTAmOT0wJjEwPTAmMTE9MCYxMj0wJjEzPTAmMTQ9MCYxNT0wJjE2PTAmMTc9MCYxOD0wJjE5PTAmMjA9MCYyMT0wJjIyPTAmMjM9MA',
    'has_more': True,
    'items': [{
        'by_user': {
            'type': 'premium',
            'usericon': 'http://a.deviantart.net/avatars/b/a/bamuth.jpg?2',
            'userid': '76954E0B-B6E2-3FDD-59BF-4B47C9B2A8C8',
            'username': 'bamuth'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'premium',
                'usericon': 'http://a.deviantart.net/avatars/b/a/bamuth.jpg?2',
                'userid': '76954E0B-B6E2-3FDD-59BF-4B47C9B2A8C8',
                'username': 'bamuth'
            },
            'category': 'Fantasy',
            'category_path': 'digitalart/paintings/people/fantasy',
            'content': {
                'filesize': 307669,
                'height': 900,
                'src': 'http://orig12.deviantart.net/08d8/f/2015/301/9/d/z1_900_by_bamuth-d9eqvas.jpg',
                'transparency': False,
                'width': 706
            },
            'deviationid': 'EBE692CA-3F68-B855-6CFA-AEB64E203324',
            'is_deleted': False,
            'is_downloadable': False,
            'is_favourited': False,
            'is_mature': False,
            'printid': None,
            'published_time': 1446095070,
            'stats': {
                'comments': 4,
                'favourites': 235
            },
            'thumbs': [{
                'height': 150,
                'src': 'http://t00.deviantart.net/LHFhdCM45Pam2rafRFdd-sXw4q4=/fit-in/150x150/filters:no_upscale():origin()/pre11/4f41/th/pre/f/2015/301/9/d/z1_900_by_bamuth-d9eqvas.jpg',
                'transparency': False,
                'width': 118
            }, {
                'height': 200,
                'src': 'http://t14.deviantart.net/g_C6LWI6CRYmVuNMTJ_Zi2weSlY=/300x200/filters:fixed_height(100,100):origin()/pre11/4f41/th/pre/f/2015/301/9/d/z1_900_by_bamuth-d9eqvas.jpg',
                'transparency': False,
                'width': 157
            }, {
                'height': 382,
                'src': 'http://t14.deviantart.net/3zuJ1uXgf17U0x5Uef4tCjayCb4=/fit-in/300x900/filters:no_upscale():origin()/pre11/4f41/th/pre/f/2015/301/9/d/z1_900_by_bamuth-d9eqvas.jpg',
                'transparency': False,
                'width': 300
            }],
            'title': 'Z1-900',
            'url': 'http://bamuth.deviantart.com/art/Z1-900-568963828'
        }],
        'ts': '2015-10-28T22:04:44-0700',
        'type': 'deviation_submitted'
    }, {
        'by_user': {
            'type': 'premium',
            'usericon': 'http://a.deviantart.net/avatars/b/u/built4ever.jpg?1',
            'userid': '5E86B832-6974-5E54-3E18-207A8088E76F',
            'username': 'Built4ever'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'premium',
                'usericon': 'http://a.deviantart.net/avatars/b/u/built4ever.jpg?1',
                'userid': '5E86B832-6974-5E54-3E18-207A8088E76F',
                'username': 'Built4ever'
            },
            'category': 'Architectural Design',
            'category_path': 'designs/architectural',
            'content': {
                'filesize': 767998,
                'height': 956,
                'src': 'http://img07.deviantart.net/2df2/i/2015/301/2/a/custom_residence_new_york_area_by_built4ever-d9eqd5w.png',
                'transparency': False,
                'width': 1280
            },
            'deviationid': '934D38FE-7254-F964-5759-F59A5EF3F07C',
            'is_deleted': False,
            'is_downloadable': False,
            'is_favourited': False,
            'is_mature': False,
            'preview': {
                'height': 772,
                'src': 'http://pre05.deviantart.net/3d69/th/pre/i/2015/301/2/a/custom_residence_new_york_area_by_built4ever-d9eqd5w.png',
                'transparency': False,
                'width': 1034
            },
            'printid': None,
            'published_time': 1446084790,
            'stats': {
                'comments': 3,
                'favourites': 42
            },
            'thumbs': [{
                'height': 112,
                'src': 'http://t10.deviantart.net/t3RuezX728dW7eRIE3j5Hg0SMiU=/fit-in/150x150/filters:no_upscale():origin()/pre05/3d69/th/pre/i/2015/301/2/a/custom_residence_new_york_area_by_built4ever-d9eqd5w.png',
                'transparency': False,
                'width': 150
            }, {
                'height': 200,
                'src': 'http://t10.deviantart.net/cDgngytBA-ivkPMGZ45_7k4Bw3c=/300x200/filters:fixed_height(100,100):origin()/pre05/3d69/th/pre/i/2015/301/2/a/custom_residence_new_york_area_by_built4ever-d9eqd5w.png',
                'transparency': False,
                'width': 268
            }, {
                'height': 224,
                'src': 'http://t13.deviantart.net/QIBBuStnfWu7035IljcBVd9WnRg=/fit-in/300x900/filters:no_upscale():origin()/pre05/3d69/th/pre/i/2015/301/2/a/custom_residence_new_york_area_by_built4ever-d9eqd5w.png',
                'transparency': False,
                'width': 300
            }],
            'title': 'Custom Residence New York Area',
            'url': 'http://built4ever.deviantart.com/art/Custom-Residence-New-York-Area-568940324'
        }],
        'ts': '2015-10-28T19:13:10-0700',
        'type': 'deviation_submitted'
    }, {
        'by_user': {
            'type': 'premium',
            'usericon': 'http://a.deviantart.net/avatars/r/a/radojavor.jpg',
            'userid': '431D1204-028D-A15B-4934-257A5A78C48C',
            'username': 'RadoJavor'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'premium',
                'usericon': 'http://a.deviantart.net/avatars/r/a/radojavor.jpg',
                'userid': '431D1204-028D-A15B-4934-257A5A78C48C',
                'username': 'RadoJavor'
            },
            'category': 'Landscapes & Scenery',
            'category_path': 'digitalart/paintings/landscapes',
            'content': {
                'filesize': 983915,
                'height': 950,
                'src': 'http://orig13.deviantart.net/e188/f/2015/301/a/7/the_storm_by_radojavor-d9eput7.jpg',
                'transparency': False,
                'width': 1600
            },
            'deviationid': '48298B16-F0D5-8F62-39B0-CF89E785F1F4',
            'is_deleted': False,
            'is_downloadable': True,
            'is_favourited': False,
            'is_mature': False,
            'preview': {
                'height': 689,
                'src': 'http://pre12.deviantart.net/026c/th/pre/f/2015/301/a/7/the_storm_by_radojavor-d9eput7.jpg',
                'transparency': False,
                'width': 1160
            },
            'printid': None,
            'published_time': 1446077064,
            'stats': {
                'comments': 24,
                'favourites': 311
            },
            'thumbs': [{
                'height': 89,
                'src': 'http://t14.deviantart.net/lvrmGzg2HEsSiiZV_f3N2xoW-II=/fit-in/150x150/filters:no_upscale():origin()/pre12/026c/th/pre/f/2015/301/a/7/the_storm_by_radojavor-d9eput7.jpg',
                'transparency': False,
                'width': 150
            }, {
                'height': 178,
                'src': 'http://t04.deviantart.net/jpQSSVNQ4UMEfzA7K6a6h9OIZvI=/300x200/filters:fixed_height(100,100):origin()/pre12/026c/th/pre/f/2015/301/a/7/the_storm_by_radojavor-d9eput7.jpg',
                'transparency': False,
                'width': 300
            }, {
                'height': 178,
                'src': 'http://t10.deviantart.net/7j_XXAEabnqADdif0Ht9gePMejA=/fit-in/300x900/filters:no_upscale():origin()/pre12/026c/th/pre/f/2015/301/a/7/the_storm_by_radojavor-d9eput7.jpg',
                'transparency': False,
                'width': 300
            }],
            'title': 'The Storm',
            'url': 'http://radojavor.deviantart.com/art/The-Storm-568916539'
        }],
        'ts': '2015-10-28T17:04:24-0700',
        'type': 'deviation_submitted'
    }, {
        'by_user': {
            'type': 'senior',
            'usericon': 'http://a.deviantart.net/avatars/d/a/danluvisiart.jpg?1',
            'userid': '3140D178-9EA9-465A-8FCB-FA7B619A82C7',
            'username': 'DanLuVisiArt'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'senior',
                'usericon': 'http://a.deviantart.net/avatars/d/a/danluvisiart.jpg?1',
                'userid': '3140D178-9EA9-465A-8FCB-FA7B619A82C7',
                'username': 'DanLuVisiArt'
            },
            'category': 'Movies & TV',
            'category_path': 'fanart/digital/drawings/movies',
            'content': {
                'filesize': 685918,
                'height': 980,
                'src': 'http://orig01.deviantart.net/84ff/f/2015/301/d/3/popped_culture_kickstarter_by_danluvisiart-d9ephd5.jpg',
                'transparency': False,
                'width': 633
            },
            'deviationid': '3DC1422E-7ECD-ED24-D6D5-08F797888EB4',
            'is_deleted': False,
            'is_downloadable': True,
            'is_favourited': False,
            'is_mature': False,
            'printid': None,
            'published_time': 1446070899,
            'stats': {
                'comments': 17,
                'favourites': 321
            },
            'thumbs': [{
                'height': 150,
                'src': 'http://t15.deviantart.net/ZoTCA27rTc69JPb0-kICOTdXtYo=/fit-in/150x150/filters:no_upscale():origin()/pre05/9ac5/th/pre/f/2015/301/d/3/popped_culture_kickstarter_by_danluvisiart-d9ephd5.jpg',
                'transparency': False,
                'width': 97
            }, {
                'height': 200,
                'src': 'http://t04.deviantart.net/gfdrik2LY2kide3smTqvxXrTgpg=/300x200/filters:fixed_height(100,100):origin()/pre05/9ac5/th/pre/f/2015/301/d/3/popped_culture_kickstarter_by_danluvisiart-d9ephd5.jpg',
                'transparency': False,
                'width': 129
            }, {
                'height': 464,
                'src': 'http://t14.deviantart.net/ZtyRCZ9pYOoum8OyyukyXnZJrxU=/fit-in/300x900/filters:no_upscale():origin()/pre05/9ac5/th/pre/f/2015/301/d/3/popped_culture_kickstarter_by_danluvisiart-d9ephd5.jpg',
                'transparency': False,
                'width': 300
            }],
            'title': 'Popped Culture Kickstarter',
            'url': 'http://danluvisiart.deviantart.com/art/Popped-Culture-Kickstarter-568899113'
        }],
        'ts': '2015-10-28T15:21:43-0700',
        'type': 'deviation_submitted'
    }, {
        'by_user': {
            'type': 'senior',
            'usericon': 'http://a.deviantart.net/avatars/d/a/danluvisiart.jpg?1',
            'userid': '3140D178-9EA9-465A-8FCB-FA7B619A82C7',
            'username': 'DanLuVisiArt'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'senior',
                'usericon': 'http://a.deviantart.net/avatars/d/a/danluvisiart.jpg?1',
                'userid': '3140D178-9EA9-465A-8FCB-FA7B619A82C7',
                'username': 'DanLuVisiArt'
            },
            'category': 'Personal',
            'category_path': 'journals/personal',
            'deviationid': '078E6027-D7BC-4E97-7CF9-6EDF08D65AA7',
            'excerpt': "I'll be launching a Kickstarter for my "
            'series Popped Culture come November '
            '1st, this Sunday, at 9AM PST.<br /><br '
            '/>Hope to see you there!<br /><br '
            '/>Follow me on IG: @danluvisiart <br '
            '/>Follow me on FB: '
            'www.facebook.com/danluvisiart ',
            'is_deleted': False,
            'is_downloadable': False,
            'is_favourited': False,
            'is_mature': False,
            'printid': None,
            'published_time': 1446070840,
            'stats': {
                'comments': 4,
                'favourites': 3
            },
            'thumbs': [],
            'title': 'Popped Culture Kickstarter',
            'url': 'http://danluvisiart.deviantart.com/journal/Popped-Culture-Kickstarter-568899033'
        }],
        'ts': '2015-10-28T15:20:41-0700',
        'type': 'journal_submitted'
    }, {
        'by_user': {
            'type': 'premium',
            'usericon': 'http://a.deviantart.net/avatars/s/h/shilin.gif?1',
            'userid': '35CF6981-1A3A-88E8-C5E0-B4D59FB8FD0A',
            'username': 'shilin'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'premium',
                'usericon': 'http://a.deviantart.net/avatars/s/h/shilin.gif?1',
                'userid': '35CF6981-1A3A-88E8-C5E0-B4D59FB8FD0A',
                'username': 'shilin'
            },
            'category': 'Personal',
            'category_path': 'journals/personal',
            'deviationid': '9024996F-AFE1-F4E8-DCE3-23DC642FFDD6',
            'excerpt': 'stream over, thanks for watching! next '
            'stream ETA: Sunday night 9pm EST on '
            'twitch.tv/adobe<br /><br '
            '/>http://twitch.tv/okolnir '
            'sketching<br /><br />SCHEDULE:<br />I '
            'stream few times a week during the day '
            'between 2-7pm EST, or 10pm-1am EST<br '
            '/>',
            'is_deleted': False,
            'is_downloadable': False,
            'is_favourited': False,
            'is_mature': False,
            'printid': None,
            'published_time': 1424621397,
            'stats': {
                'comments': 30,
                'favourites': 62
            },
            'thumbs': [],
            'title': '[ended] livestreaming! twitch.tv/okolnir',
            'url': 'http://shilin.deviantart.com/journal/ended-livestreaming-twitch-tv-okolnir-515765528'
        }],
        'ts': '2015-10-28T13:26:18-0700',
        'type': 'journal_submitted'
    }, {
        'by_user': {
            'type': 'regular',
            'usericon': 'http://a.deviantart.net/avatars/n/i/nikyeliseyev.jpg?2',
            'userid': 'D92952F7-FFBD-3262-13E3-7DCEB407CC45',
            'username': 'NikYeliseyev'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'regular',
                'usericon': 'http://a.deviantart.net/avatars/n/i/nikyeliseyev.jpg?2',
                'userid': 'D92952F7-FFBD-3262-13E3-7DCEB407CC45',
                'username': 'NikYeliseyev'
            },
            'category': 'Conceptual',
            'category_path': 'traditional/paintings/illustration/conceptual',
            'content': {
                'filesize': 193954,
                'height': 664,
                'src': 'http://img14.deviantart.net/7a1e/i/2015/301/7/4/112_by_nikyeliseyev-d9eozx7.jpg',
                'transparency': False,
                'width': 1024
            },
            'deviationid': '5DD7431B-402C-2A0C-ABC4-009333438BB9',
            'is_deleted': False,
            'is_downloadable': True,
            'is_favourited': False,
            'is_mature': False,
            'printid': None,
            'published_time': 1446063971,
            'stats': {
                'comments': 0,
                'favourites': 32
            },
            'thumbs': [{
                'height': 97,
                'src': 'http://t04.deviantart.net/KcTQqCoDkwXmgL8gdrB0YDKATDQ=/fit-in/150x150/filters:no_upscale():origin()/pre08/4b5a/th/pre/i/2015/301/7/4/112_by_nikyeliseyev-d9eozx7.jpg',
                'transparency': False,
                'width': 150
            }, {
                'height': 195,
                'src': 'http://t02.deviantart.net/awVtIaXRV15yIgABZb4WEBVHmnY=/300x200/filters:fixed_height(100,100):origin()/pre08/4b5a/th/pre/i/2015/301/7/4/112_by_nikyeliseyev-d9eozx7.jpg',
                'transparency': False,
                'width': 300
            }, {
                'height': 195,
                'src': 'http://t01.deviantart.net/vueEffHoSb0ob2AuMImcTMCFBgQ=/fit-in/300x900/filters:no_upscale():origin()/pre08/4b5a/th/pre/i/2015/301/7/4/112_by_nikyeliseyev-d9eozx7.jpg',
                'transparency': False,
                'width': 300
            }],
            'title': '112',
            'url': 'http://nikyeliseyev.deviantart.com/art/112-568876507'
        }],
        'ts': '2015-10-28T13:26:11-0700',
        'type': 'deviation_submitted'
    }, {
        'by_user': {
            'type': 'regular',
            'usericon': 'http://a.deviantart.net/avatars/w/a/warrenlouw.jpg?6',
            'userid': '7B234243-1A78-28EA-E11B-10CFAA7D8D79',
            'username': 'WarrenLouw'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'regular',
                'usericon': 'http://a.deviantart.net/avatars/w/a/warrenlouw.jpg?6',
                'userid': '7B234243-1A78-28EA-E11B-10CFAA7D8D79',
                'username': 'WarrenLouw'
            },
            'category': 'Conceptual',
            'category_path': 'digitalart/paintings/illustrations/conceptual',
            'content': {
                'filesize': 1097412,
                'height': 895,
                'src': 'http://orig11.deviantart.net/8831/f/2015/300/6/1/jace_highborn_by_warren_louw_by_warrenlouw-d9elhsh.png',
                'transparency': True,
                'width': 750
            },
            'deviationid': '0F7E2B8E-DC7D-0744-A59F-92900BC80DA4',
            'is_deleted': False,
            'is_downloadable': True,
            'is_favourited': False,
            'is_mature': False,
            'printid': None,
            'published_time': 1445984915,
            'stats': {
                'comments': 20,
                'favourites': 839
            },
            'thumbs': [{
                'height': 150,
                'src': 'http://t01.deviantart.net/0WTxdGQsLwGAxaD7PJ8M4bTzgrk=/fit-in/150x150/filters:no_upscale():origin()/pre04/9af0/th/pre/f/2015/300/6/1/jace_highborn_by_warren_louw_by_warrenlouw-d9elhsh.png',
                'transparency': True,
                'width': 126
            }, {
                'height': 200,
                'src': 'http://t10.deviantart.net/IZvNKxIBt-79IADO8mvt0gJH3os=/300x200/filters:fixed_height(100,100):origin()/pre04/9af0/th/pre/f/2015/300/6/1/jace_highborn_by_warren_louw_by_warrenlouw-d9elhsh.png',
                'transparency': True,
                'width': 168
            }, {
                'height': 358,
                'src': 'http://t00.deviantart.net/7TH9CfnY8h3gQXwRSOgkfF_DoT4=/fit-in/300x900/filters:no_upscale():origin()/pre04/9af0/th/pre/f/2015/300/6/1/jace_highborn_by_warren_louw_by_warrenlouw-d9elhsh.png',
                'transparency': True,
                'width': 300
            }],
            'title': 'Jace Highborn by Warren Louw',
            'url': 'http://warrenlouw.deviantart.com/art/Jace-Highborn-by-Warren-Louw-568713041'
        }],
        'ts': '2015-10-27T15:28:35-0700',
        'type': 'deviation_submitted'
    }, {
        'by_user': {
            'type': 'premium',
            'usericon': 'http://a.deviantart.net/avatars/s/h/shilin.gif?1',
            'userid': '35CF6981-1A3A-88E8-C5E0-B4D59FB8FD0A',
            'username': 'shilin'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'premium',
                'usericon': 'http://a.deviantart.net/avatars/s/h/shilin.gif?1',
                'userid': '35CF6981-1A3A-88E8-C5E0-B4D59FB8FD0A',
                'username': 'shilin'
            },
            'category': 'Drawings',
            'category_path': 'manga/digital/drawings',
            'content': {
                'filesize': 939815,
                'height': 1100,
                'src': 'http://orig10.deviantart.net/518f/f/2015/300/2/9/my_dear_daughter_by_shilin-d9ele87.png',
                'transparency': False,
                'width': 733
            },
            'deviationid': 'DBA0A7B6-339A-9240-B637-3BD69BC72751',
            'is_deleted': False,
            'is_downloadable': True,
            'is_favourited': False,
            'is_mature': False,
            'preview': {
                'height': 1095,
                'src': 'http://pre06.deviantart.net/6db1/th/pre/f/2015/300/2/9/my_dear_daughter_by_shilin-d9ele87.png',
                'transparency': False,
                'width': 730
            },
            'printid': '62AAE6A3-CEFA-3747-CC32-05B060F43C4D',
            'published_time': 1445983828,
            'stats': {
                'comments': 84,
                'favourites': 5009
            },
            'thumbs': [{
                'height': 150,
                'src': 'http://t15.deviantart.net/1YbPcP2wh0PwQcHH9Jf0IjWGB9M=/fit-in/150x150/filters:no_upscale():origin()/pre06/6db1/th/pre/f/2015/300/2/9/my_dear_daughter_by_shilin-d9ele87.png',
                'transparency': False,
                'width': 100
            }, {
                'height': 200,
                'src': 'http://t06.deviantart.net/uopd7M2E5cQ1XnBdfT4BP5MoQxw=/300x200/filters:fixed_height(100,100):origin()/pre06/6db1/th/pre/f/2015/300/2/9/my_dear_daughter_by_shilin-d9ele87.png',
                'transparency': False,
                'width': 133
            }, {
                'height': 450,
                'src': 'http://t12.deviantart.net/xh9gFnf_7h-Wrf_YBz6W0eizDwc=/fit-in/300x900/filters:no_upscale():origin()/pre06/6db1/th/pre/f/2015/300/2/9/my_dear_daughter_by_shilin-d9ele87.png',
                'transparency': False,
                'width': 300
            }],
            'title': 'My dear daughter',
            'url': 'http://shilin.deviantart.com/art/My-dear-daughter-568708423'
        }],
        'ts': '2015-10-27T15:10:30-0700',
        'type': 'deviation_submitted'
    }, {
        'by_user': {
            'type': 'premium',
            'usericon': 'http://a.deviantart.net/avatars/l/i/liiga.jpg?1',
            'userid': 'A4EC5D8F-D84B-B620-4BDD-2A4FE1015AA6',
            'username': 'liiga'
        },
        'deviations': [{
            'allows_comments': True,
            'author': {
                'type': 'premium',
                'usericon': 'http://a.deviantart.net/avatars/l/i/liiga.jpg?1',
                'userid': 'A4EC5D8F-D84B-B620-4BDD-2A4FE1015AA6',
                'username': 'liiga'
            },
            'category': 'Fantasy',
            'category_path': 'digitalart/paintings/fantasy',
            'content': {
                'filesize': 487142,
                'height': 722,
                'src': 'http://orig07.deviantart.net/6e6f/f/2015/300/c/2/nad06_12185_phoenix_liigasmilshkalne_rgb_dasmall_by_liiga-d9el5ko.jpg',
                'transparency': False,
                'width': 1100
            },
            'deviationid': '3729FEA5-0A86-0375-7140-9E063C880701',
            'is_deleted': False,
            'is_downloadable': False,
            'is_favourited': False,
            'is_mature': False,
            'printid': 'C21C1FF2-341B-F335-3AE8-B6141F90D037',
            'published_time': 1445979838,
            'stats': {
                'comments': 16,
                'favourites': 251
            },
            'thumbs': [{
                'height': 98,
                'src': 'http://t11.deviantart.net/Jl6MMmcGcY_maM4Osg8OcS8kDR0=/fit-in/150x150/filters:no_upscale():origin()/pre12/62e6/th/pre/f/2015/300/c/2/nad06_12185_phoenix_liigasmilshkalne_rgb_dasmall_by_liiga-d9el5ko.jpg',
                'transparency': False,
                'width': 150
            }, {
                'height': 197,
                'src': 'http://t01.deviantart.net/YpkBujH71psOrFpVYOE-yeMqphI=/300x200/filters:fixed_height(100,100):origin()/pre12/62e6/th/pre/f/2015/300/c/2/nad06_12185_phoenix_liigasmilshkalne_rgb_dasmall_by_liiga-d9el5ko.jpg',
                'transparency': False,
                'width': 300
            }, {
                'height': 197,
                'src': 'http://t05.deviantart.net/eFHR1RAaSMsIphq17xGUDQHz5lA=/fit-in/300x900/filters:no_upscale():origin()/pre12/62e6/th/pre/f/2015/300/c/2/nad06_12185_phoenix_liigasmilshkalne_rgb_dasmall_by_liiga-d9el5ko.jpg',
                'transparency': False,
                'width': 300
            }],
            'title': 'Android - Phoenix',
            'url': 'http://liiga.deviantart.com/art/Android-Phoenix-568697208'
        }],
        'ts': '2015-10-27T14:03:58-0700',
        'type': 'deviation_submitted'
    }]
}


def main():
    app.run(debug=True, port=58008)


if __name__ == '__main__':
    main()
