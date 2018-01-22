# What is this?

I stumbled across this ftp: 

    ftp://ftp.modland.com/pub/modules/Protracker/Supernao/
    
And wanted to download some of the favorite collections from it. But the files were all stored as separate mods, no zip bundles or similar. So, I decided to take some 20 mins off and write my own python downloader, that takes input param url, and output param 'where to save', and it would simply go through all the links and download each of them using wget. 

It uses cli to invoke curl, awk and wget, I didn't want to waste time reinventing the wheel, those cmds all work like a charm, and I have been using them whenever I had a similar situation. 


# Example usage

    # this will suck all of the modules from Supernao page and store them
    # in the ./downloads/supernao folder
    ./modsucker -i ftp://ftp.modland.com/pub/modules/Protracker/Supernao/ ./downloads/supernao
    
    
# Limitations

Currently no support for recursive download. I.e. folders will probably be ignored.     
    