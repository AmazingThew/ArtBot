#ARTBOT
Needs a better name


#WHAT IS THIS
It's a tool that scrapes art websites (currently Pixiv, DeviantArt, and ArtStation), pulling down the full-res images and displaying them in a nice dynamically updating column view.


#WHY
Manually checking a bunch of separate art websites is a pain because you have to be like "NOW I WILL LOOK AT ART" and then dedicate time to it. A single page that just auto-updates with the latest images twitter-style is way nicer.
 
...Also Pixiv's UX is horrific


#DID YOU JUST PAINSTAKINGLY REINVENT RSS FEEDS
Pretty much yes, but I was nearly finished by the time I noticed that
(Real answer: UX is way different from RSS. Focused entirely on artwork and otherwise staying as far out of your way as possible)


#CURRENT STATUS
Works p well imo


#HOW TO USE
* Have Python 3.x
* Use pip or your IDE or whatever to install all the modules you don't already have
* Copy exampleConfig.json to a new file, name it config.json, add your login info to the appropriate fields and tweak obvious settings if desired
* Yes it requires you to just dump your pixiv password into a plaintext config file leave me alone
* Run `main.py`
* Point your browser at localhost:58008 (or whatever port you put in the config, but FIVEBOOB is obviously the best choice)
* DA uses OAuth so it'll run you through that instead of using the config file
* It will check for new images every two minutes. There's a subtle countdown bar on the left side of the screen to indicate when the next check will take place
* That's all but it probably won't work because you broke it somehow


#NOTES
I'd advise running it locally rather than on a remote server. Pixiv is incredibly dedicated to preventing hotlinks so ArtBot actually just downloads the images to disk and serves them from there. Depending on your hosting (and how many artists you follow) this could amount to nontrivial bandwidth.
Also there's currently almost no error handling of any kind; if something goes wrong you'll have to check the Python terminal and/or the JS console in your browser. Log files are for sissies.


#TODO
* Add a "favorites" view. This would be a second (collapsible) feed that shows works that have been liked/fav'd by the artists you follow. Pixiv's API can support this, but I don't think DA's will and ArtStation will need to be scraped for it. Probably a fairly significant amount of work but would be SUPER nice to have. Browsing favs is usually an awesome way to find new artists.
* Parallelization. Currently checking for new artwork takes forever bc it has to make like a hundred GET requests and wait for all the responses serially.
* This would however, lead to non-trivial CPU usage, which would in turn suggest running the whole thing on a home server, which IN TURN requires:
* Proper logging/error handling
