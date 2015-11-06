import json
import shelve

from flask import Flask, redirect, send_file, jsonify, request, render_template

from loaders.deviantart import DeviantArt, DeviantArtApiError
from loaders.pixiv import Pixiv


expiredToken = 'b5d4098c2683a7a5e89adf728b424feab3678b84a81c586b0b'

DA_AUTH_REDIRECT = '/deviantartAuthorizationRedirect'

PIXIV_DOWNLOAD_DIRECTORY = 'static/downloaded'

USE_PIXIV      = True
USE_DEVIANTART = True


class ArtBot(object):

    def __init__(self, shelf):
        self.app = Flask(__name__, static_folder='static')

        self.shelf = shelf

        if USE_PIXIV: self.pixiv = Pixiv(self.shelf, PIXIV_DOWNLOAD_DIRECTORY)
        if USE_DEVIANTART: self.deviantart = DeviantArt(self.shelf, 'http://localhost:58008'+DA_AUTH_REDIRECT)

        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/getWorks', 'getWorks', self.getWorks)
        self.app.add_url_rule('/getLoginDetails', 'getLoginDetails', self.getLoginDetails)
        self.app.add_url_rule('/submitLoginDetails', 'submitLoginDetails', self.submitLoginDetails, methods=['POST'])
        self.app.add_url_rule('/authorizeDeviantart', 'authorizeDeviantart', self.authorizeDeviantart)
        self.app.add_url_rule(DA_AUTH_REDIRECT, 'deviantartAuthorizationRedirect', self.deviantartAuthorizationRedirect)

        self.app.register_error_handler(DeviantArtApiError, self.handle_invalid_usage)

        self.app.run(debug=True, port=58008)


    def index(self):
        if USE_PIXIV and not (self.shelf.get('pixivUsername') and self.shelf.get('pixivPassword')):
            return redirect('/getLoginDetails')
        return send_file('static/index.html')


    def getLoginDetails(self):
        return send_file('static/loginDetails.html')


    def submitLoginDetails(self):
        self.shelf['pixivUsername'] = request.form['pixivUsername']
        self.shelf['pixivPassword'] = request.form['pixivPassword']
        if USE_PIXIV: self.pixiv.authorize()
        return redirect('/')


    def getWorks(self):
        works = []
        if USE_DEVIANTART: works.extend(self.deviantart.getWorks())
        if USE_PIXIV:      works.extend(self.pixiv.getWorks())
        # pprint(works)

        self.shelf.sync()
        return json.dumps(works)

        # return pixivTestWorks
        # return json.dumps(deviantart.parseFeed(lold))
        # return deviantartTestWorks
        # return json.dumps(pixiv.getWorks())


    def persistWorks(self):
        pass


    def authorizeDeviantart(self):
        return render_template('authorizeDeviantart.html', url=self.deviantart.getAuthorizationUrl())
        # return '<a href="{0}"><h1>DeviantArt needs authorization</h1></a>'.format(deviantart.getAuthorizationUrl())


    def deviantartAuthorizationRedirect(self):
        self.deviantart.handleAuthorizationCallback(request)
        return redirect('/')


    def handle_invalid_usage(self, error):
        print('ERROR HANDLING')
        print(error.message)
        print(self.deviantart.token)
        response = jsonify(error.message)
        response.status_code = error.status_code
        return response

def main():
    with shelve.open('db', writeback=True) as shelf:
        # shelf['deviantartToken'] = 'fart'
        # shelf['deviantartRefreshToken'] = 'also fart'
        # shelf['pixivUsername'] = ''
        # shelf['pixivPassword'] = ''
        ArtBot(shelf)

pixivTestWorks      = '''[{"imageUrls": ["http://i2.pixiv.net/img-original/img/2015/10/31/01/19/26/53289625_p0.png"], "width": "703", "nsfw": "False", "authorName": "\u30bf\u30ab\u30e4\u30de@\u30c6\u30a3\u30a2K26ab", "profileUrl": "http://www.pixiv.net/member.php?id=37577", "identifier": "25576ad0-01ea-403e-9016-2cab056748ce", "imageTitle": "\u30cf\u30c3\u30d4\u30fc\u30cf\u30ed\u30a6\u30a3\u30f3", "authorAvatarUrl": "http://i2.pixiv.net/img04/profile/takayama7/1334141_s.jpg", "authorHandle": "takayama7", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-31 01:19:26", "height": "1000", "website": "Pixiv"}, {"imageUrls": ["http://i3.pixiv.net/img-original/img/2015/10/31/00/06/01/53286946_p0.png"], "width": "2500", "nsfw": "False", "authorName": "lack", "profileUrl": "http://www.pixiv.net/member.php?id=83739", "identifier": "4a00af21-5ec4-4309-836f-22652b0c3f53", "imageTitle": "Halloween sky", "authorAvatarUrl": "http://i1.pixiv.net/img09/profile/blacklack-21/1370342_s.jpg", "authorHandle": "blacklack-21", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-31 00:06:01", "height": "1768", "website": "Pixiv"}, {"imageUrls": ["http://i2.pixiv.net/img-original/img/2015/10/30/04/28/03/53273849_p0.png"], "width": "1500", "nsfw": "False", "authorName": "\u3082\u3082\u3053", "profileUrl": "http://www.pixiv.net/member.php?id=1113943", "identifier": "82d48326-fdd5-4729-be5c-8eb7bbe13927", "imageTitle": "happy halloween!", "authorAvatarUrl": "http://i3.pixiv.net/img37/profile/momopoco/9172583_s.png", "authorHandle": "momopoco", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-30 04:28:03", "height": "2125", "website": "Pixiv"}, {"imageUrls": ["http://i3.pixiv.net/img-original/img/2015/10/30/00/09/09/53270650_p0.png"], "width": "1414", "nsfw": "False", "authorName": "lack", "profileUrl": "http://www.pixiv.net/member.php?id=83739", "identifier": "8cf142c2-97ef-4e94-9619-84f9317b4499", "imageTitle": "\u9ed2\u3044\u96e8\u8d64\u3044\u5098", "authorAvatarUrl": "http://i1.pixiv.net/img09/profile/blacklack-21/1370342_s.jpg", "authorHandle": "blacklack-21", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-30 00:09:09", "height": "2000", "website": "Pixiv"}, {"imageUrls": ["http://i4.pixiv.net/img-original/img/2015/10/29/00/01/43/53256087_p0.png"], "width": "2500", "nsfw": "False", "authorName": "lack", "profileUrl": "http://www.pixiv.net/member.php?id=83739", "identifier": "20881792-acf7-44a4-82ff-d073fec7ffb8", "imageTitle": "\u304a\u83d3\u5b50\u306a\u304a\u8336\u4f1a", "authorAvatarUrl": "http://i1.pixiv.net/img09/profile/blacklack-21/1370342_s.jpg", "authorHandle": "blacklack-21", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-29 00:01:43", "height": "1050", "website": "Pixiv"}, {"imageUrls": ["http://i2.pixiv.net/img-original/img/2015/10/28/21/12/36/53242489_p0.png"], "width": "1414", "nsfw": "False", "authorName": "lack", "profileUrl": "http://www.pixiv.net/member.php?id=83739", "identifier": "ffb51526-50f5-462f-bcae-f145873e4bc4", "imageTitle": "\u8d64\u9ed2\u9aa8\u5b9d\u9928", "authorAvatarUrl": "http://i1.pixiv.net/img09/profile/blacklack-21/1370342_s.jpg", "authorHandle": "blacklack-21", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-28 00:02:45", "height": "2000", "website": "Pixiv"}, {"imageUrls": ["http://i3.pixiv.net/img-original/img/2015/10/26/00/01/49/53214258_p0.png"], "width": "1414", "nsfw": "False", "authorName": "lack", "profileUrl": "http://www.pixiv.net/member.php?id=83739", "identifier": "3a9a1fb9-5cf2-4035-950a-0bd194e328c4", "imageTitle": "\u95c7\u76ee\u305f\u3061\u306e\u5bb4", "authorAvatarUrl": "http://i1.pixiv.net/img09/profile/blacklack-21/1370342_s.jpg", "authorHandle": "blacklack-21", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-26 00:00:45", "height": "2000", "website": "Pixiv"}, {"imageUrls": ["http://i2.pixiv.net/img-original/img/2015/10/25/17/07/06/53204845_p0.png", "http://i2.pixiv.net/img-original/img/2015/10/25/17/07/06/53204845_p1.png"], "width": "650", "nsfw": "False", "authorName": "Krenz", "profileUrl": "http://www.pixiv.net/member.php?id=74646", "identifier": "31e7139b-e520-46e3-9c15-dc9f017f7382", "imageTitle": "OurJourney", "authorAvatarUrl": "http://i2.pixiv.net/img08/profile/krenz/439153_s.jpg", "authorHandle": "krenz", "imageType": "manga", "success": "False", "error": "None", "imageTimestamp": "2015-10-25 17:07:06", "height": "919", "website": "Pixiv"}, {"imageUrls": ["http://i2.pixiv.net/img-original/img/2015/10/25/00/00/40/53193617_p0.png"], "width": "1768", "nsfw": "False", "authorName": "lack", "profileUrl": "http://www.pixiv.net/member.php?id=83739", "identifier": "6baf5518-49f4-4864-a4c5-0a505b924cb7", "imageTitle": "\u77e5\u6075\u8005\u306e\u5de3", "authorAvatarUrl": "http://i1.pixiv.net/img09/profile/blacklack-21/1370342_s.jpg", "authorHandle": "blacklack-21", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-25 00:00:40", "height": "2500", "website": "Pixiv"}, {"imageUrls": ["http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p0.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p1.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p2.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p3.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p4.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p5.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p6.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p7.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p8.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p9.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p10.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p11.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p12.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p13.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p14.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p15.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p16.png", "http://i3.pixiv.net/img-original/img/2015/10/24/00/00/46/53176554_p17.png"], "width": "700", "nsfw": "False", "authorName": "lack", "profileUrl": "http://www.pixiv.net/member.php?id=83739", "identifier": "ed654393-d070-423b-a797-6b281176e778", "imageTitle": "\u30e9\u30af\u30ac\u30ad\u306a\u3069\u307e\u3068\u3081\uff13", "authorAvatarUrl": "http://i1.pixiv.net/img09/profile/blacklack-21/1370342_s.jpg", "authorHandle": "blacklack-21", "imageType": "manga", "success": "False", "error": "None", "imageTimestamp": "2015-10-24 00:00:46", "height": "1036", "website": "Pixiv"}, {"imageUrls": ["http://i2.pixiv.net/img-original/img/2015/10/23/12/26/35/53167905_p0.png"], "width": "1843", "nsfw": "False", "authorName": "PIGEON", "profileUrl": "http://www.pixiv.net/member.php?id=793999", "identifier": "dcc4dfa3-53d1-46a9-8444-f61928faac3b", "imageTitle": "\u9244\u8840\u306e\u30aa\u30eb\u30d5\u30a7\u30f3\u30ba", "authorAvatarUrl": "http://i2.pixiv.net/img30/profile/pigeon666/7546004_s.png", "authorHandle": "pigeon666", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-23 12:26:35", "height": "1682", "website": "Pixiv"}, {"imageUrls": ["http://i3.pixiv.net/img-original/img/2015/10/18/00/19/07/53086722_p0.png"], "width": "2000", "nsfw": "False", "authorName": "PIGEON", "profileUrl": "http://www.pixiv.net/member.php?id=793999", "identifier": "cee188e6-878d-4da6-a883-44d051c834ca", "imageTitle": "\u7f8e\u5c11\u5973\u6226\u58eb", "authorAvatarUrl": "http://i2.pixiv.net/img30/profile/pigeon666/7546004_s.png", "authorHandle": "pigeon666", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-18 00:19:07", "height": "1124", "website": "Pixiv"}, {"imageUrls": ["http://i4.pixiv.net/img-original/img/2015/10/12/00/07/24/52992223_p0.png"], "width": "990", "nsfw": "False", "authorName": "\u6751\u5c71\u7adc\u5927", "profileUrl": "http://www.pixiv.net/member.php?id=16666", "identifier": "149fd227-e4f7-4e15-a48f-4227ddf38f30", "imageTitle": "\u6c17\u914d", "authorAvatarUrl": "http://i4.pixiv.net/img02/profile/ovopack/9958930_s.png", "authorHandle": "ovopack", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-12 00:07:24", "height": "1400", "website": "Pixiv"}, {"imageUrls": ["http://i4.pixiv.net/img-original/img/2015/10/06/14/20/25/52899499_p0.png"], "width": "1033", "nsfw": "False", "authorName": "PIGEON", "profileUrl": "http://www.pixiv.net/member.php?id=793999", "identifier": "0a41deeb-199d-481e-9f5d-0d94dc2c8d45", "imageTitle": "Chen sagan", "authorAvatarUrl": "http://i2.pixiv.net/img30/profile/pigeon666/7546004_s.png", "authorHandle": "pigeon666", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-06 14:20:25", "height": "921", "website": "Pixiv"}, {"imageUrls": ["http://i2.pixiv.net/img-original/img/2015/10/06/14/18/14/52899485_p0.png"], "width": "1000", "nsfw": "True", "authorName": "PIGEON", "profileUrl": "http://www.pixiv.net/member.php?id=793999", "identifier": "8e55b908-3040-47d9-80a7-67f6168e1a1e", "imageTitle": "9", "authorAvatarUrl": "http://i2.pixiv.net/img30/profile/pigeon666/7546004_s.png", "authorHandle": "pigeon666", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-06 14:18:14", "height": "1415", "website": "Pixiv"}, {"imageUrls": ["http://i3.pixiv.net/img-original/img/2015/10/04/21/21/55/52873218_p0.png"], "width": "873", "nsfw": "False", "authorName": "\u6751\u5c71\u7adc\u5927", "profileUrl": "http://www.pixiv.net/member.php?id=16666", "identifier": "3afe5dfe-1ea3-4826-9a91-855580393252", "imageTitle": "\u7adc\u4f7f\u3044\u306e\u5c11\u5e74", "authorAvatarUrl": "http://i4.pixiv.net/img02/profile/ovopack/9958930_s.png", "authorHandle": "ovopack", "imageType": "illustration", "success": "False", "error": "None", "imageTimestamp": "2015-10-04 21:21:55", "height": "1400", "website": "Pixiv"}]'''
deviantartTestWorks = '''[{"nsfw": "False", "profileUrl": "http://bamuth.deviantart.com", "error": "", "authorHandle": "bamuth", "imageTimestamp": "2015-10-28T22:04:44-0700", "imageType": "\"deviation\"", "success": "True", "website": "DeviantArt", "imageTitle": "Z1-900", "width": "706", "authorAvatarUrl": "http://a.deviantart.net/avatars/b/a/bamuth.jpg?2", "authorName": "bamuth", "identifier": "EBE692CA-3F68-B855-6CFA-AEB64E203324", "height": "900", "imageUrls": ["http://orig12.deviantart.net/08d8/f/2015/301/9/d/z1_900_by_bamuth-d9eqvas.jpg"]}, {"nsfw": "False", "profileUrl": "http://Built4ever.deviantart.com", "error": "", "authorHandle": "Built4ever", "imageTimestamp": "2015-10-28T19:13:10-0700", "imageType": "\"deviation\"", "success": "True", "website": "DeviantArt", "imageTitle": "Custom Residence New York Area", "width": "1280", "authorAvatarUrl": "http://a.deviantart.net/avatars/b/u/built4ever.jpg?1", "authorName": "Built4ever", "identifier": "934D38FE-7254-F964-5759-F59A5EF3F07C", "height": "956", "imageUrls": ["http://img07.deviantart.net/2df2/i/2015/301/2/a/custom_residence_new_york_area_by_built4ever-d9eqd5w.png"]}, {"nsfw": "False", "profileUrl": "http://RadoJavor.deviantart.com", "error": "", "authorHandle": "RadoJavor", "imageTimestamp": "2015-10-28T17:04:24-0700", "imageType": "\"deviation\"", "success": "True", "website": "DeviantArt", "imageTitle": "The Storm", "width": "1600", "authorAvatarUrl": "http://a.deviantart.net/avatars/r/a/radojavor.jpg", "authorName": "RadoJavor", "identifier": "48298B16-F0D5-8F62-39B0-CF89E785F1F4", "height": "950", "imageUrls": ["http://orig13.deviantart.net/e188/f/2015/301/a/7/the_storm_by_radojavor-d9eput7.jpg"]}, {"nsfw": "False", "profileUrl": "http://DanLuVisiArt.deviantart.com", "error": "", "authorHandle": "DanLuVisiArt", "imageTimestamp": "2015-10-28T15:21:43-0700", "imageType": "\"deviation\"", "success": "True", "website": "DeviantArt", "imageTitle": "Popped Culture Kickstarter", "width": "633", "authorAvatarUrl": "http://a.deviantart.net/avatars/d/a/danluvisiart.jpg?1", "authorName": "DanLuVisiArt", "identifier": "3DC1422E-7ECD-ED24-D6D5-08F797888EB4", "height": "980", "imageUrls": ["http://orig01.deviantart.net/84ff/f/2015/301/d/3/popped_culture_kickstarter_by_danluvisiart-d9ephd5.jpg"]}, {"nsfw": "False", "profileUrl": "http://NikYeliseyev.deviantart.com", "error": "", "authorHandle": "NikYeliseyev", "imageTimestamp": "2015-10-28T13:26:11-0700", "imageType": "\"deviation\"", "success": "True", "website": "DeviantArt", "imageTitle": "112", "width": "1024", "authorAvatarUrl": "http://a.deviantart.net/avatars/n/i/nikyeliseyev.jpg?2", "authorName": "NikYeliseyev", "identifier": "5DD7431B-402C-2A0C-ABC4-009333438BB9", "height": "664", "imageUrls": ["http://img14.deviantart.net/7a1e/i/2015/301/7/4/112_by_nikyeliseyev-d9eozx7.jpg"]}, {"nsfw": "False", "profileUrl": "http://WarrenLouw.deviantart.com", "error": "", "authorHandle": "WarrenLouw", "imageTimestamp": "2015-10-27T15:28:35-0700", "imageType": "\"deviation\"", "success": "True", "website": "DeviantArt", "imageTitle": "Jace Highborn by Warren Louw", "width": "750", "authorAvatarUrl": "http://a.deviantart.net/avatars/w/a/warrenlouw.jpg?6", "authorName": "WarrenLouw", "identifier": "0F7E2B8E-DC7D-0744-A59F-92900BC80DA4", "height": "895", "imageUrls": ["http://orig11.deviantart.net/8831/f/2015/300/6/1/jace_highborn_by_warren_louw_by_warrenlouw-d9elhsh.png"]}, {"nsfw": "False", "profileUrl": "http://shilin.deviantart.com", "error": "", "authorHandle": "shilin", "imageTimestamp": "2015-10-27T15:10:30-0700", "imageType": "\"deviation\"", "success": "True", "website": "DeviantArt", "imageTitle": "My dear daughter", "width": "733", "authorAvatarUrl": "http://a.deviantart.net/avatars/s/h/shilin.gif?1", "authorName": "shilin", "identifier": "DBA0A7B6-339A-9240-B637-3BD69BC72751", "height": "1100", "imageUrls": ["http://orig10.deviantart.net/518f/f/2015/300/2/9/my_dear_daughter_by_shilin-d9ele87.png"]}, {"nsfw": "False", "profileUrl": "http://liiga.deviantart.com", "error": "", "authorHandle": "liiga", "imageTimestamp": "2015-10-27T14:03:58-0700", "imageType": "\"deviation\"", "success": "True", "website": "DeviantArt", "imageTitle": "Android - Phoenix", "width": "1100", "authorAvatarUrl": "http://a.deviantart.net/avatars/l/i/liiga.jpg?1", "authorName": "liiga", "identifier": "3729FEA5-0A86-0375-7140-9E063C880701", "height": "722", "imageUrls": ["http://orig07.deviantart.net/6e6f/f/2015/300/c/2/nad06_12185_phoenix_liigasmilshkalne_rgb_dasmall_by_liiga-d9el5ko.jpg"]}]'''

if __name__ == '__main__':
    main()
    # main()