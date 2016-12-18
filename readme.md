#ARTBOT
Needs a better name


#WHAT IS THIS
It's a tool that scrapes art websites (currently Pixiv and DeviantArt, hopefully more eventually), pulling down the full-res images and displaying them in a nice dynamically updating column view.


#WHY
Manually checking a bunch of separate art websites is a pain because you have to be like "NOW I WILL LOOK AT ART" and then dedicate time to it. A single page that just auto-updates with the latest images twitter-style is way nicer.
 
...Also Pixiv's UX is horrific


#DID YOU JUST PAINSTAKINGLY REINVENT RSS FEEDS
Pretty much yes, but I was nearly finished by the time I noticed that


#CURRENT STATUS
Very alpha. It works for DA and Pixiv at the moment but hasn't really been bug tested and a lot of planned features are missing.
The UI is kinda pretty though
  
  
  
#HOW TO USE
* Have Python 3.x
* TBH just use PyCharm or something so it can auto-install whatever Python libraries you don't already have; pip is annoying
* For some reason the [Pixiv API module](https://github.com/upbit/pixivpy) is named pixivpy3 but the pip package is named pixivpy so it screws up PyCharm's auto-import. Either `pip install pixivpy` or change the line where it imports `pixivpy3` to say `import pixivpy` so that PyCharm can install it and then change it back
* Run `main.py`
* Point your browser at localhost:58008
* It'll ask you for your Pixiv login details (over an unsecured connection and subsequently stored as plaintext for maximum Web Dev), and then send you to DA to authorize through their fancy OAuth thing
* It will check for new images every two minutes. There's a subtle countdown bar on the left side of the screen to indicate when the next check will take place
* That's all but it probably won't work because you broke it somehow


#NOTES
I'd advise running it locally rather than on a remote server. Besides the aforementioned lack of SSL Pixiv is incredibly dedicated to preventing hotlinks so ArtBot actually just downloads the images to disk and serves them from there. Depending on your hosting (and how many artists you follow) this could amount to nontrivial bandwidth.
Also there's currently almost no error handling of any kind; if something goes wrong you'll have to check the Python terminal and/or the JS console in your browser. Log files are for sissies.
 
 
#TODO
* Support Pixiv manga pages properly. They display all screwy right now
* Proper logging/error handling
* Add support for ArtStation. This is going to SUCK because they don't have a public API, and their site is mostly javascript so scraping it will require spinning up some kind of actual browsery thing to render the page first.
  * (ArtStation has a mobile app so there's presumably an API of SOME sort. Someone could probably take apart the Android app and/or figure out the API via Wireshark but that's more work than I have time for)
* Add a "favorites" view. This would be a second (collapsible) feed that shows works that have been liked/fav'd by the artists you follow. Pixiv's API can support this, but I don't think DA's will and ArtStation will need to be scraped for it. Probably a fairly significant amount of work but would be SUPER nice to have. Browsing favs is usually an awesome way to find new artists.
* Also one time the image dimensions got all screwed up on reload and I have no idea why and can't reproduce it but hey that's probably a bug that should be fixed I guess 
