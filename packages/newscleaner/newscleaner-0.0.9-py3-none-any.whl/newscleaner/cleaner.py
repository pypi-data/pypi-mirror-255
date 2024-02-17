#!/usr/bin/env python
# coding: utf-8
#cleaner function 0.0.9

# In[3]:


# importing all the important libraries
import re
import json
import html
import unicodedata
import pkg_resources


# In[4]:


#  Cleaning raw HTML and retaining tags
def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def replace_all1(text, dic):
    for i, j in dic.items():
        text = text.replace(j, i)
    return text

def cleaner(text):

    tags = {'<p>' : '{p}', '</p>':'{/p}','<span>': '{span}','</span>':'{/span}', '<br>':'{br}','</br>':'{/br}','<b>':'{b}',
            '</b>':'{/b}','<i>':'{i}','</i>':'{/i}','<u>':'{u}','</u>':'{/u}' ,'<strong>':'{strong}','</strong>':'{/strong}' ,
            '<h1>':'{h1}','</h1>':'{/h1}','<h2>':'{h2}','</h2>':'{/h2}','<h3>':'{h3}','</h3>':'{/h3}','<h4>':'{h4}',
            '</h4>':'{/h4}','<h5>':'{h5}','</h5>':'{/h5}','<h6>':'{h6}','</h6>':'{/h6}', '<li>':'{li}','</li>':'{/li}',
            '<ol>':'{ol}', '</ol>':'{/ol}', '<img':'{img', '}>':'}}'}

    clean_text = re.sub("""(<img)+[a-zA-Z\d\s=":/.?\-;&,_{}!–@#“”$%^*()_+=\[\]|\\'~`‘’]+(>)""", "<img_tags_retained>", text)

    clean_text = re.sub("""(<img_tags_retained>[Õa-zA-ZI=".\s\d&“”#-;{},:_'?|–@#!~`$’%^&*()\-_=+\[\]]*<)""",'<img_tags_retained><',clean_text) #removing image caption
    clean_text = re.sub("""(<img_tags_retained>[Õa-zA-ZI=".\s\d&“”#-;,:_'?|–@#!~`$’%^&*()\-_=+\[\]]*<\/p>[\s]*[a-zA-Z/:]*[\s]*[a-zA-Z/:]*[\s]*[a-zA-Z/:]*[\s]*<)""",'<img_tags_retained><',clean_text) #removing image caption
    clean_text = re.sub("""(</strong>[\s]*<strong>)""",'',clean_text) #removing consecutive strong-tags

    if "<img_tags_retained>" in clean_text:
        img_tags = clean_text.split("<img_tags_retained>")
        img_tag_list = []
        stop = len(img_tags)-1
        for ind,i in enumerate(img_tags):
            img_tag_list.append(i)
            if ind != stop:
                img_tag_list.append("{img src={IMG_" + str(ind) + "}>")

        clean_text = "".join(img_tag_list)

    clean_text = replace_all(clean_text, tags)
    # display(clean_text)


    clean_text = re.sub(r'<[^<>]*>', ' ',clean_text) #removing all html tags
    # display(clean_text)
    clean_text = re.sub('http[s]?://\S+', ' ', clean_text) # removing all urls
    # display(clean_text)
    clean_text = re.sub('\S*@\S*\s?', '',clean_text) #removing all links
    clean_text = re.sub('\|*Advertisement\|*','',clean_text) #removing Advertisement keyword
    clean_text = re.sub('\|*(Getty Images)\|*','',clean_text) #removing getty images keyword


    # Removing Pattern from independent.uk.co
    clean_text = re.sub(".*" + "r {{ /verifyErrors }}", '', clean_text)
    clean_text = re.sub(".*" + "Washington email" , '', clean_text)
    clean_text = re.sub(".*" + "breaking news emails", '', clean_text)
    clean_text = re.sub(".*" + "for all the latest news", '', clean_text)
    clean_text = re.sub(".*" + "This email for free", '', clean_text)
    clean_text = re.sub(".*" + "Check email", '', clean_text)
    clean_text = re.sub(".*" + "Headlines email", '', clean_text)

    # msnbc pattern removal
    clean_text = re.sub("Tweet us " + ".*",'',clean_text)
    clean_text = re.sub("You can read more" + ".*",'', clean_text)

    #greenwich & ourmidland time pattern removal
    clean_text = re.sub("This is a carousel. Use Next and Previous buttons to navigate",'',clean_text)
    clean_text = re.sub("Show More",'',clean_text)
    clean_text = re.sub("Show Less",'',clean_text)

    #NJ.com
    clean_text = re.sub("Our journalism needs your support" + ".*",'',clean_text)
    clean_text = re.sub("For NJ Advance",'',clean_text)
    clean_text = re.sub("COPYRIGHT 2023 CREATORS.COM",'',clean_text)
    clean_text = re.sub("Thank you for relying on us to provide" + ".*",'',clean_text)
    clean_text = re.sub("RELATED STORIES " + ".*",'',clean_text)
    clean_text = re.sub("The N.J. High School Sports newsletter" + ".*",'',clean_text)

    #nbcsports
    clean_text = re.sub("Subscribe to and rate" + ".*",'',clean_text)
    clean_text = re.sub(" Click here to follow the " + ".*",'',clean_text)
    clean_text = re.sub(" Download and follow the" + ".*",'',clean_text)

    #newsweek
    clean_text = re.sub("(}[\s]*Getty[\s]*{)",'}{',clean_text)
    clean_text = re.sub("Newsweek reached out to" + ".*",'',clean_text)
    clean_text = re.sub("Newsweek has reached out to" + ".*",'',clean_text)

    #click2houston
    #pattern_c2 = "___" + ".*"
    #clean_text = re.sub(pattern_c2,'',clean_text)

    #clickorlando
    clean_text = re.sub("Get today’s headlines in minutes with",'',clean_text)
    clean_text = re.sub("Your Florida Daily",'',clean_text)
    clean_text = re.sub("Click here for more information about" + ".*",'',clean_text)
    clean_text = re.sub("FILE - ",'',clean_text)

    #cleveland.com
    clean_text = re.sub(" See video of the play here ",'',clean_text)
    clean_text = re.sub("Get police blotters by email every weekday for free with our new Police Blotter newsletter."  + ".*",'',clean_text)
    clean_text = re.sub("Ad not displaying properly?" + ".*",'',clean_text)
    clean_text = re.sub("Get a jumpstart on the weekend. Sign up for Cleveland.com ’s" + ".*",'',clean_text)
    clean_text = re.sub("Read more of her work" + ".*",'',clean_text)

    #nbcboston
    clean_text = re.sub("Get Boston local news, weather forecasts, lifestyle and entertainment stories to your inbox.","",clean_text)
    clean_text = re.sub("’s newsletters.","",clean_text)
    clean_text = re.sub("Read the full story on NBCNews.com here.","",clean_text)
    clean_text = re.sub("Get Boston local news, weather forecasts, lifestyle and entertainment stories to your inbox. ’s newsletters.",'',clean_text)

    #nbcchicago
    clean_text = re.sub("Get Chicago local news, weather forecasts, sports and entertainment stories to your inbox.","",clean_text)
    clean_text = re.sub("Read the full story on NBCNews.com here.","",clean_text)
    clean_text = re.sub("Download MyTeams Today!","",clean_text)
    clean_text = re.sub("""(}[\s]*Click here to)+[a-zA-Z=".\s\d&#-;,|<>:_'’]*({)""","",clean_text)
    clean_text = re.sub("Be sure to download the NBC Chicago app on your Apple or Android devices , or you can tune into the NBC 5 newscasts throughout the afternoon for the latest weather information.","",clean_text)
    clean_text = re.sub("For all the latest information, stay tuned to the NBC"+".*",'',clean_text)

    #nbcdfw
    clean_text = re.sub("Read the full story at NBCNews.com","",clean_text)
    clean_text = re.sub("Editor's note: All odds are provided by our partner, PointsBet ."+".*","",clean_text)
    clean_text = re.sub(" This story first appeared on TODAY.com . More from TODAY: ","",clean_text)

    #cnbc
    clean_text = re.sub("Subscribe\xa0 here \xa0to get this report sent directly to your inbox each morning before markets open. ","",clean_text)
    clean_text = re.sub("watch now","",clean_text)
    clean_text = re.sub("Getty Images Entertainment | Getty Images","",clean_text)

    #wgntv
    clean_text = re.sub("Suggest a Correction","",clean_text)
    clean_text = re.sub("This is a developing story, follow"+".*","",clean_text)

    #fox2news
    clean_text = re.sub("You can find out more at"+".*","",clean_text)
    clean_text = re.sub("This story will be updated throughout the day.","",clean_text)
    clean_text = re.sub(r"The Conversation","",clean_text)
    clean_text = re.sub(r'(-)+', r'\1',clean_text)

    #nbcmiami
    clean_text = re.sub("Get South Florida local news, weather forecasts and entertainment stories to your inbox.","",clean_text)
    clean_text = re.sub(" More information on how to apply can be found here .","",clean_text)
    clean_text = re.sub("This story first appeared on TODAY.com."+".*","",clean_text)

    clean_text = re.sub('\|*(Image source, )\|*','',clean_text) #removing bbc errors
    clean_text = re.sub('\|*(Image caption, )\|*','',clean_text) #removing bbc errors
    clean_text = re.sub('\|*(More on this story)\|*.+','',clean_text) #removing bbc errors
    clean_text = re.sub('\|*(Sign up for )\|*[a-z\sA-Z]+','',clean_text) #removing bbc errors
    clean_text = re.sub('\|*(Sign up to )\|*[a-z\sA-Z]+','',clean_text) #removing bbc errors

    clean_text = re.sub('\|*(This content is created and maintained by a third party, )\|*.+','',clean_text) #removing cosmopliton error
    clean_text = re.sub('\|*(Download it for )\|*[a-z\sA-Z]+','',clean_text) #removing cosmopliton error
    clean_text = re.sub('({Android})','{}',clean_text) #removing cosmopliton error
    #clean_text = re.sub('(Follow )+\S+( on ).+','',clean_text) #removing cosmopliton error
    #clean_text = re.sub('(>Instagram<)','><',clean_text) #removing Advertisement keyword

    clean_text = re.sub('\|*(A version of this story appeared in the )\|*[a-z\sA-Z0-9.]+','',clean_text) #removing hollywood error
    clean_text = re.sub('\|*(Click here to subscribe.)\|*','',clean_text) #removing hollywood error

    clean_text = re.sub('\|*(For weekly email updates on\nresidential real estate news, )\|*.+','',clean_text) #removing nytimes error


    clean_text = re.sub("""(}[\s]*(More News)+[Õa-zA-Z=".\s\d&#-;,:_'?|@’!~`$%^&*“”(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing stamfordadvocate error of entire text after sentence starting with "More News" keyword
    clean_text = re.sub("""(}[\s]*(More Entertainment)+[Õa-zA-Z=".\s\d&-;,:_'?|@#’!~`$%^&*“”(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing stamfordadvocate error of entire text after sentence starting with "More Entertainment" keyword
    clean_text = re.sub("""({p}}[\s]*(UP NEXT)+[Õa-zA-Z=".\s\d&-;,:_'?|@#’!~`$%^&*“”(){}<>\-_=+\[\]]+)""",'',clean_text) #removing stamfordadvocate error of entire text after sentence starting with "UP NEXT" keyword
    clean_text = re.sub("""(}[\s]*(___)+[Õa-zA-Z=".\s\d&-;,:_'?|@#’!~`$%^&*“”(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing stamfordadvocate error of entire text after sentence starting with "___" keyword
    clean_text = re.sub('\|*(This is a carousel. Use Next and Previous buttons to navigate)\|*','',clean_text) #removing stamfordadvocate error

    #clean_text = re.sub("\|*(Top news)\|*[a-z</>\sA-Z'-.0-9:_‘’|“”$–?.-…{}]+",'',clean_text) #removing thegurdian error

    clean_text = re.sub('\|*(Required reading)\|*','',clean_text) #removing theatheletic error
    clean_text = re.sub("\|*(GO DEEPER{)\|*[/}a-zA-Z\s,'0-9:]+",'',clean_text) #removing theatheletic error

    clean_text = re.sub("\|*([A-Z])\|*[A-Z0-9\s',:.-]{20,}",'',clean_text) #removing foxnews error
    clean_text = re.sub("(NEW{)+[/a-zA-Z\s}!]+",'',clean_text) #removing foxnews error
    clean_text = re.sub('(}[\s]*Advertising[\s]*{)','}{',clean_text) #removing "Advertising" keyword

    clean_text = re.sub('(}[\s]*Advertising[\s]*{)','}{',clean_text) #removing "Advertising" keyword
    clean_text = re.sub("""([\s]*Also read[\s]*{/p})+[a-zA-Z{}=".\s\d&#-;,|<>:_'].+({/p})""",'',clean_text) #removing one para after "Also read" keyword
    clean_text = re.sub('(For more lifestyle news).+','',clean_text) #removing text after "For more lifestyle news" keyword
    clean_text = re.sub('(}[\s]*\(With inputs from agencies\)[\s]*{)','}{',clean_text) #removing "(With inputs from agencies)" keywords
    clean_text = re.sub('(({p}[\s]*Read)+[a-zA-Z{}=".\s\d&#-;,<>]+(on The Eastern Herald.))+[a-zA-Z{}=".\s\d&#-;,<>]+','',clean_text) #removing Last Lines in Eastern Herald keyword
    clean_text = re.sub("""(\{p\}\{strong\}[\s]*Also Read \|)+[a-zA-Z{}=".\s\d&#-;,<>:'?|@!~`$%^&*()_=+\[\]]+(\{/strong\}\{/p\})""",'',clean_text) #removing one para after "Also Read" keyword
    clean_text = re.sub("""({p}[\s]*SHARE THIS ARTICLE ON[\s]*{/p})+[a-zA-Z{}=".\s\d&#-;,*^@$!()+\[\]~`<>:_'\n?%]+""",'',clean_text) #removing text after "SHARE THIS ARTICLE ON" keyword
    clean_text = re.sub("""(\([\s]*Also read \|)+[a-zA-Z{}=".\s\d&#-;,<>:_']+(\))""",'',clean_text) #removing one para after "Also read |" keyword
    clean_text = re.sub("""(}[\s]*Also read:)+[a-zA-Z{}=".\s\d&#-;,<>:_']+({/a}{/p})""",'}',clean_text) #removing one para after "Also read:" keyword
    clean_text = re.sub("""(}[\s]*ALSO READ:)+[a-zA-Z{}=".\s\d&#-;,<>:_']+({/a}{/p})""",'}',clean_text) #removing one para after "ALSO READ: " keyword
    clean_text = re.sub("""(}[\s]*Also Read:)+[a-zA-Z{}=".\s\d&#-;,<>:_']+{/a}{/p}""",'}',clean_text) #removing one para after "ALSO READ: " keyword
    clean_text = re.sub("""(Also read \|)+[a-zA-Z{}=".\s\d&#-;,<>:_'?]+({/a})""",'',clean_text) #removing one para after "Also read |" keyword
    clean_text = re.sub("""([\s]*Source:)+[\sA-Za-z.]+""",'',clean_text) #removing "Source:" keyword
    clean_text = re.sub("""(}[\s]*top videos[\s]*{)""",'}{',clean_text) #removing "top videos" keyword
    clean_text = re.sub("""(ALSO READ\|)+[a-zA-Z{}=".\s\d&#-;,<>:_'?]+({/a})""",'',clean_text) #removing one para after "ALSO READ|" keyword
    clean_text = re.sub("""(}[\s]*Read all the)+[a-zA-Z{}=".\s\d&#-;,<>:()_]+(here[\s]*{/p})+[a-zA-Z{}=".\s\d&#-;,<>:()_]+""",'}',clean_text) #removing text after "Read all the ... here" keyword

    clean_text = re.sub("""(\{strong\}[\s]*ALSO READ \|)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+\{/strong\}""",'',clean_text) #removing one para after "ALSO READ |" keyword
    clean_text = re.sub("""(\{strong\}\{b\}[\s]*ALSO READ[\s]*\{/b\})+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+\{/strong\}""",'',clean_text) #removing one para after "ALSO READ |" keyword
    clean_text = re.sub('(}[\s]*advertisement[\s]*{)','}{',clean_text) #removing "advertisement" keyword
    clean_text = re.sub("""(}--- ENDS ---{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "--- ENDS ---" keyword
    clean_text = re.sub("""(}[\s]*Read here:)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+{/a}{/p}""",'}',clean_text) #removing "Read here:" keyword
    clean_text = re.sub("""(}[\s]*\(With inputs from ANI\)[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "(With inputs from ANI)" keyword
    clean_text = re.sub("""(}[\s]*\(With PTI inputs\)[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "(With PTI inputs)" keyword
    clean_text = re.sub("""(}[\s]*ABOUT THE AUTHOR[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "(ABOUT THE AUTHOR)" keyword
    clean_text = re.sub("""(\{strong\}[\s]*Also Read \|)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+\{/strong\}\{/a\}""",'',clean_text) #removing one para after "Also Read |" keyword
    clean_text = re.sub("""(}[\s]*\(With inputs from PTI, ANI\)[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "(With PTI inputs)" keyword

    # display(clean_text)
    clean_text = re.sub(r'{p}{strong}Watch This Story:&#160;{/strong}.*?{/strong} {/p}', '', clean_text, flags=re.DOTALL)

    clean_text = re.sub("""(\{p\}\{strong\}[\s]*WATCH \|[\s]*\{/strong\}\{/p\})""",'',clean_text) #removing "WATCH |" keyword
    clean_text = re.sub("""(\{p\}\{strong\}[\s]*ALSO WATCH \|[\s]*\{/strong\}\{/p\})""",'',clean_text) #removing "WATCH |" keyword
    clean_text = re.sub("""(}[\s]*ADVERTISEMENT[\s]*{)""",'}{',clean_text) #removing "ADVERTISEMENT" keyword
    clean_text = re.sub("""(}[\s]*Express News Service[\s]*{)""",'}{',clean_text) #removing "Express News Service" keyword
    clean_text = re.sub("""(}[\s]*Online Desk[\s]*{)""",'}{',clean_text) #removing "Online Desk" keyword
    clean_text = re.sub(""".+([\s]*By[\s]*{)""",'{',clean_text) #removing text before "By" keyword
    clean_text = re.sub("""(}[\s]*AFP[\s]*{)""",'}{',clean_text) #removing "AFP" keyword
    clean_text = re.sub("""(}[\s]*PTI[\s]*{)""",'}{',clean_text) #removing "PTI" keyword
    clean_text = re.sub("""(}[\s]*ANI[\s]*{)""",'}{',clean_text) #removing "ANI" keyword
    clean_text = re.sub("""(}[\s]*IANS[\s]*{)""",'}{',clean_text) #removing "IANS" keyword
    #clean_text = re.sub("""(}[\s]*View this post on Instagram[\s]*{)""",'}{',clean_text) #removing text "View this post on Instagram" keyword
    clean_text = re.sub("""(}[\s]*Latest Entertainment News[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "(With PTI inputs)" keyword
    #clean_text = re.sub("""([\s]*Follow us on Image Source INSTAGRAM[\s]*{)""",'{',clean_text) #removing text "Follow us on Image Source INSTAGRAM" keyword
    #clean_text = re.sub("""([\s]*Follow us on Image Source TWITTER[\s]*{)""",'{',clean_text) #removing text "Follow us on Image Source TWITTER" keyword
    clean_text = re.sub("""(}[\s]*Read More Trending News[\s]*{)""",'}{',clean_text) #removing text "Read More Trending News" keyword
    clean_text = re.sub("""(}[\s]*Here's how they reacted.[\s]*{)""",'}{',clean_text) #removing text "Here's how they reacted." keyword
    clean_text = re.sub("""(}[\s]*Check out the photos here-[\s]*{)""",'}{',clean_text) #removing text "Check out the photos here-" keyword
    clean_text = re.sub("""(}[\s]*Unsplash[\s]*{)""",'}{',clean_text) #removing "Unsplash" keyword
    clean_text = re.sub("""(}[\s]*Screenshot[\s]*{)""",'}{',clean_text) #removing "Screenshot" keyword
    clean_text = re.sub("""(}[\s]*screenshot[\s]*{)""",'}{',clean_text) #removing "screenshot" keyword
    clean_text = re.sub("""(}[\s]*Agencies[\s]*{)""",'}{',clean_text) #removing "Agencies" keyword
    #clean_text = re.sub("""(}[\s]*Twitter[\s]*{)""",'}{',clean_text) #removing "Twitter" keyword
    #clean_text = re.sub("""(}[\s]*TWITTER[\s]*{)""",'}{',clean_text) #removing "TWITTER" keyword
    #clean_text = re.sub("""(}[\s]*Reddit[\s]*{)""",'}{',clean_text) #removing "Reddit" keyword
    #clean_text = re.sub("""(}[\s]*Instagram[\s]*{)""",'}{',clean_text) #removing "Instagram" keyword
    #clean_text = re.sub("""(}[\s]*INSTAGRAM[\s]*{)""",'}{',clean_text) #removing "INSTAGRAM" keyword
    #clean_text = re.sub("""(}[\s]*Facebook[\s]*{)""",'}{',clean_text) #removing "Facebook" keyword
    #clean_text = re.sub("""(}[\s]*FACEBOOK[\s]*{)""",'}{',clean_text) #removing "FACEBOOK" keyword
    #clean_text = re.sub("""(}[\s]*Telegram[\s]*{)""",'}{',clean_text) #removing "Telegram" keyword
    #clean_text = re.sub("""(}[\s]*TELEGRAM[\s]*{)""",'}{',clean_text) #removing "TELEGRAM" keyword
    clean_text = re.sub("""(}[\s]*web screen grab[\s]*{)""",'}{',clean_text) #removing "web screen grab" keyword
    clean_text = re.sub("""(}[\s]*Reuters[\s]*{)""",'}{',clean_text) #removing "Reuters" keyword
    clean_text = re.sub("""(}[\s]*What do you think about it? Do let us know in the comments.[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "What do you think about it? Do let us know in the comments." keyword
    clean_text = re.sub("""(}[\s]*Click here .[\s]*{)""",'}{',clean_text) #removing "Click here ." keyword

    clean_text = re.sub("""(}[\s]*Poll[\s]*{)+[{}a-z/\s]+(}[\s]*0 votes[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "Poll 0 votes" keyword
    clean_text = re.sub("""([\s]*Leave your thoughts in the comments section below.[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'',clean_text) #removing text after "Leave your thoughts in the comments section below." keyword
    clean_text = re.sub("""(}[\s]*Check out the full video below[\s]*{)""",'}{',clean_text) #removing "Check out the full video below" keyword
    #clean_text = re.sub("""(\}[\s]*Read all the \{strong\} Latest News \{/strong\}, \{strong\} Trending News \{/strong\}, \{strong\} Cricket News \{/strong\}, \{strong\} Bollywood News \{/strong\}, \{strong\} India News \{/strong\} and \{strong\} Entertainment News \{/strong\} here. Follow us on Facebook , Twitter and Instagram .\{/p\})""",'}',clean_text) #removing "Read all the Latest News , Trending News , Cricket News , Bollywood News , India News and Entertainment News here. Follow us on Facebook , Twitter and Instagram ." keyword
    clean_text = re.sub("""(}[\s]*Related[\s]*{)""",'}{',clean_text) #removing "Related" keyword
    clean_text = re.sub("""({b}IPL 2023{/b} {b} . {/b} {b}Dream11 Prediction{/b} {b} . {/b} {b}Fantasy Cricket Tips{/b} {b} . {/b} {b}Cricket Match Prediction Today{/b} {b} . {/b} {b}Cricket News{/b} {b} . {/b} {b}Cricket Live Score{/b})""",'',clean_text) #removing "IPL 2023 . Dream11 Prediction . Fantasy Cricket Tips . Cricket Match Prediction Today . Cricket News . Cricket Live Score" keyword
    clean_text = re.sub("""({b}IPL 2023{/b} {b} .{/b} {b}India National Cricket Team{/b} {b}. {/b} {b}Chennai Super Kings {/b} {b} . {/b} {b}Delhi Capitals {/b} {b} . {/b} {b}Gujarat Titans {/b} {b} . {/b} {b}Kolkata Knight Riders {/b} {b} . {/b} {b}Lucknow Supergiants {/b} {b} . {/b} {b}Mumbai Indians {/b} {b} . {/b} {b}Punjab Kings {/b} {b} . {/b} {b}Rajasthan Royals {/b} {b} . {/b} {b}Royal Challengers Bangalore {/b} {b} . {/b} {b}SunRisers Hyderabad {/b})""",'',clean_text) #removing "IPL 2023 . India National Cricket Team . Chennai Super Kings . Delhi Capitals . Gujarat Titans . Kolkata Knight Riders . Lucknow Supergiants . Mumbai Indians . Punjab Kings . Rajasthan Royals . Royal Challengers Bangalore . SunRisers Hyderabad" keyword
    clean_text = re.sub("""({b}Virat Kohli{/b} {b} . {/b} {b}Rohit Sharma{/b} {b} . {/b} {b}Rishabh Pant{/b} {b} . {/b} {b}KL Rahul{/b} {b} . {/b} {b}Suryakumar Yadav{/b} {b} . {/b} {b}Sanju Samson{/b} {b} . {/b} {b}Shreyas Iyer{/b} {b} . {/b} {b}Yuzvendra Chahal{/b} {b} . {/b} {b}Jasprit Bumrah{/b})""",'',clean_text) #removing "Virat Kohli . Rohit Sharma . Rishabh Pant . KL Rahul . Suryakumar Yadav . Sanju Samson . Shreyas Iyer . Yuzvendra Chahal . Jasprit Bumrah" keyword
    clean_text = re.sub("""(}[\s]*Follow InsideSport on GOOGLE NEWS[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "Follow InsideSport on GOOGLE NEWS" keyword
    clean_text = re.sub("""(}[\s]*Here’s the video[\s]*{)""",'}{',clean_text) #removing "Here’s the video" keyword
    clean_text = re.sub("""(}[\s]*Here is the video[\s]*{)""",'}{',clean_text) #removing "Here is the video" keyword
    clean_text = re.sub("""(}[\s]*Stay tuned to BollywoodLife for the latest scoops and updates from Bollywood , Hollywood , South , TV and Web-Series .[\s]*{)""",'}{',clean_text) #removing "Stay tuned to BollywoodLife for the latest scoops and updates from Bollywood , Hollywood , South , TV and Web-Series ." keyword
    #clean_text = re.sub("""(}[\s]*Click to join us on Facebook , Twitter , Youtube and Instagram .[\s]*{)""",'}{',clean_text) #removing "Click to join us on Facebook , Twitter , Youtube and Instagram ." keyword
    #clean_text = re.sub("""(}[\s]*Also follow us on Facebook Messenger for latest updates.[\s]*{)""",'}{',clean_text) #removing "Also follow us on Facebook Messenger for latest updates." keyword
    clean_text = re.sub("""(}[\s]*Click Here To Read/Download Order[\s]*{)""",'}{',clean_text) #removing "Click Here To Read/Download Order" keyword
    clean_text = re.sub("""(}[\s]*Click Here To Read/Download Judgement[\s]*{)""",'}{',clean_text) #removing "Click Here To Read/Download Judgement" keyword

    clean_text = re.sub("""(}[\s]*View this post on Instagram[\s]*{)""",'}{',clean_text) #removing text "View this post on Instagram" keyword
    clean_text = re.sub("""(}[\s]*SHARE[\s]*{)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing text after "SHARE" keyword
    clean_text = re.sub("""(}[\s]*Also read)+[a-zA-Z{}=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]‘’]+({)""",'}{',clean_text) #removing text "Also read" keyword
    clean_text = re.sub("""(}[\s]*READ NOW[\s]*{)""",'}{',clean_text) #removing before "READ NOW" keyword
    clean_text = re.sub("""(}[\s]*Also read)""",'}',clean_text) #removing before "READ NOW" keyword

    clean_text = re.sub("""(}[\s]*Listen[\s]*{\/p})+[a-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+({\/p}[\s]*Comment[\s]*{\/p})""",'}',clean_text) #removing text between "Listen" and "Comment" keyword
    clean_text = re.sub("""([\s]*Comment[\s]*{)""",'{',clean_text) #removing "Comment" keyword
    clean_text = re.sub("""(}[\s]*Gift Article[\s]*{)""",'}{',clean_text) #removing "Gift Article" keyword
    clean_text = re.sub("""(}[\s]*Share[\s]*{)""",'}{',clean_text) #removing "Share" keyword
    clean_text = re.sub("""(}[\s]*Listen[\s]*{)""",'}{',clean_text) #removing "Listen" keyword
    clean_text = re.sub("""(}[\s]*ArrowRight[\s]*{)""",'}{',clean_text) #removing "ArrowRight" keyword
    clean_text = re.sub("""(}[\s]*Loading...[\s]*{)""",'}{',clean_text) #removing "Loading..." keyword
    clean_text = re.sub("""(}[\s]*Never miss a goal or a touchdown. .[\s]*{)""",'}{',clean_text) #removing "Never miss a goal or a touchdown. ." keyword
    clean_text = re.sub("""(}[\s]*Wp Get the full experience. Choose your plan[\s]*{)""",'}{',clean_text) #removing "Wp Get the full experience. Choose your plan" keyword

    clean_text = re.sub("""(}[\s]*SEE MORE:[\s]*)+[a-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing para starting with "SEE MORE:" keyword
    clean_text = re.sub("""(}[\s]*See More:[\s]*)+[a-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing para starting with "See More:" keyword
    clean_text = re.sub("""([\s]*Trending stories at Scrippsnews.com[\s]*{)""",'{',clean_text) #removing "Trending stories at Scrippsnews.com" keyword
    clean_text = re.sub("""(}[\s]*LOOK BACK:[\s]*)+[a-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing para starting with "LOOK BACK:" keyword
    clean_text = re.sub("""([\s]*Subscribe to our weekly newsletter, In The Know, to get entertainment news sent straight to your inbox.[\s]*{)""",'{',clean_text) #removing "Subscribe to our weekly newsletter, In The Know, to get entertainment news sent straight to your inbox." keyword
    clean_text = re.sub("""(}[\s]*©[\s]*)+[a-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing para starting with "©" keyword
    clean_text = re.sub("""(}[\s]*Copyright ©[\s]*)+[a-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing para starting with "Copyright ©" keyword

    clean_text = re.sub("""(}[\s]*Click to email a link to a friend \(Opens in new window\)[\s]*{)""",'}{',clean_text) #removing "Click to email a link to a friend (Opens in new window)" keyword
    #clean_text = re.sub("""(}[\s]*Click to share on Twitter \(Opens in new window\)[\s]*{)""",'}{',clean_text) #removing "Click to share on Twitter (Opens in new window)" keyword
    #clean_text = re.sub("""(}[\s]*Click to share on Facebook \(Opens in new window\)[\s]*{)""",'}{',clean_text) #removing "Click to share on Facebook (Opens in new window)" keyword
    clean_text = re.sub("""(}[\s]*For more Page Six[\s]*)+[a-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$%^&*()\-_=+\[\]]+""",'}',clean_text) #removing para starting with "For more Page Six" keyword

    clean_text = re.sub("""(}[\s]*Get the inside scoop on today’s biggest stories in business, from Wall Street to Silicon Valley — delivered daily.[\s]*{)""",'}{',clean_text) #removing "Get the inside scoop on today’s biggest stories in business, from Wall Street to Silicon Valley — delivered daily." keyword
    clean_text = re.sub("""(}[\s]*Loading Something is loading.[\s]*{)""",'}{',clean_text) #removing "Loading Something is loading." keyword
    clean_text = re.sub("""(}[\s]*Thanks for signing up![\s]*{)""",'}{',clean_text) #removing "Thanks for signing up!" keyword
    clean_text = re.sub("""(}[\s]*Access your favorite topics in a personalized feed while you're on the go.[\s]*{)""",'}{',clean_text) #removing "Access your favorite topics in a personalized feed while you're on the go." keyword
    clean_text = re.sub("""(}[\s]*Email address[\s]*{)""",'}{',clean_text) #removing "Email address" keyword
    clean_text = re.sub("""(}[\s]*By clicking ‘Sign up’, you agree to receive marketing emails from Insider as well as other partner offers and accept our Terms of Service and Privacy Policy[\s]*{)""",'}{',clean_text) #removing "By clicking ‘Sign up’, you agree to receive marketing emails from Insider as well as other partner offers and accept our Terms of Service and Privacy Policy" keyword

    clean_text = re.sub("""(}[\s]*Enlarge this image[\s]*{)""",'}{',clean_text) #removing "Enlarge this image" keyword
    clean_text = re.sub("""({b}*toggle caption[\s]*{/b}{/b}[\s]*{/p}[\sa-zA-Z\d/]*{/p})""",'',clean_text) #removing "toggle caption" keyword and one para after that keyword
    clean_text = re.sub("""(}[\s]*(Email us at)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`’$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "Email us at" keyword

    clean_text = re.sub("""(}[\s]*[\[\]\d/]+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`$%^&’*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "[1/8]" or [1:4] etc. keyword
    clean_text = re.sub("""(}[\s]*Our Standards: The Thomson Reuters Trust Principles.[\s]*{)""",'}{',clean_text) #removing "Our Standards: The Thomson Reuters Trust Principles." keywords

    clean_text = re.sub("""(}[\s]*(Reporting by)+[Õa-zA-Z=".\s\d&#-;,:_'?|“@#!~`$%^&*’(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "Reporting by" keyword
    clean_text = re.sub("""(}[\s]*(Editing by)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`$%^&*’(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "Editing by" keyword
    clean_text = re.sub("""(}[\s]*-Field Level Media[\s]*{)""",'}{',clean_text) #removing "-Field Level Media" keyword
    clean_text = re.sub("""(}[\s]*- Field Level Media[\s]*{)""",'}{',clean_text) #removing "- Field Level Media" keyword
    clean_text = re.sub("""(}[\s]*The opinions expressed here are those of the author, a columnist for Reuters.[\s]*{)""",'}{',clean_text) #removing "The opinions expressed here are those of the author, a columnist for Reuters." keyword

    clean_text = re.sub("""(}[\s]*LOADING[\s]*{)""",'}{',clean_text) #removing "LOADING" keyword
    clean_text = re.sub("""(}[\s]*Loading[\s]*{)""",'}{',clean_text) #removing "Loading" keyword
    clean_text = re.sub("""(}[\s]*loading[\s]*{)""",'}{',clean_text) #removing "loading" keyword
    clean_text = re.sub("""(}[\s]*ERROR LOADING[\s]*{)""",'}{',clean_text) #removing "ERROR LOADING" keyword
    clean_text = re.sub("""(}[\s]*Error Loading[\s]*{)""",'}{',clean_text) #removing "Error Loading" keyword
    clean_text = re.sub("""(}[\s]*error loading[\s]*{)""",'}{',clean_text) #removing "error loading" keyword
    clean_text = re.sub("""(}[\s]*‘’[\s]*{)""",'}{',clean_text) #removing "error loading" keyword

    clean_text = re.sub("""(}[\s]*Show Caption[\s]*{)""",'}{',clean_text) #removing "Show Caption" keyword
    clean_text = re.sub("""(}[\s]*Hide Caption[\s]*{)""",'}{',clean_text) #removing "Hide Caption" keyword
    clean_text = re.sub("""(}[\s]*Accuweather[\s]*{)""",'}{',clean_text) #removing "Accuweather" keyword
    clean_text = re.sub("""(}[\s]*AP[\s]*{)""",'}{',clean_text) #removing "AP" keyword
    clean_text = re.sub("""(}[\s]*(Contributing:)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|“@#’!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "Contributing:" keyword
    clean_text = re.sub("""(}[\s]*(Follow USA TODAY)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|’@“#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "Follow USA TODAY" keyword
    clean_text = re.sub("""(({strong}[\s]*Watch )+[Õa-zA-Z=".\s\d&#-;,<>:_'?|“@#!~’`$%^&*()\-_=+\[\]]+{/strong})""",'',clean_text) #removing sentence starting with "<strong>Watch" keyword

    clean_text = re.sub("""(}[\s]*(Check out:)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`$%^&*()’{}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "Check out" keyword
    clean_text = re.sub("""(}[\s]*(CHECK OUT:)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`$%^&*()’{}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "CHECK OUT" keyword
    clean_text = re.sub("""(}[\s]*(check out:)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`$%^&*()’{}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "check out" keyword
    clean_text = re.sub("""(}[\s]*(Check Out:)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`$%^&*’(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "Check Out" keyword
    clean_text = re.sub("""(}[\s]*(DON'T MISS:)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`$%^’&*(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "DON'T MISS:" keyword
    clean_text = re.sub("""(}[\s]*(don't miss:)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`$%’^&*(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "don't miss:" keyword
    clean_text = re.sub("""(}[\s]*(Don't Miss:)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`$’%^&*(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "Don't Miss:" keyword
    clean_text = re.sub("""(}[\s]*(Don't miss:)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#!~`’$%^&*(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "Don't miss:" keyword
    clean_text = re.sub("""(}[\s]*In this article[\s]*{)""",'}{',clean_text) #removing "In this article" keyword
    clean_text = re.sub("""(}[\s]*(Get CNBC's free)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@’#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "Get CNBC's free" keyword
    clean_text = re.sub("""(}[\s]*(Like this story)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|’@#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "Like this story" keyword
    clean_text = re.sub("""(}[\s]*(This report)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@#!’~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "This report" keyword
    clean_text = re.sub("""(}[\s]*[A-Z]{1,5}[\s]*{)""",'}{',clean_text) #removing keywords with with length between 1 to 5

    #clean_text = re.sub("""(}[\s]*(Follow us on Twitter)+[Õa-zA-Z=".\s\d&#-;,:_'?|@“#’!~`$%^&*(){}<>\-_=+\[\]]+)""",'}',clean_text) #removing entire text after sentence starting with "Follow us on Twitter" keyword
    clean_text = re.sub("""(}[\s]*(Presented by)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`$%’^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Presented by" keyword
    clean_text = re.sub("""(}[\s]*(Presented By)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`$’%^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Presented By" keyword
    clean_text = re.sub("""(}[\s]*(PRESENTED BY)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`’$%^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "PRESENTED BY" keyword
    clean_text = re.sub("""(}[\s]*(FOLLOW US)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`$%’^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "FOLLOW US++++" keyword
    clean_text = re.sub("""(}[\s]*(Follow Us)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`$’%^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Follow Us" keyword
    clean_text = re.sub("""(}[\s]*(Follow us)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`’$%^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Follow us" keyword

    # This code given below
    # clean_text = re.sub("""(}[\s]*(For more information)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@’#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "For more information" keyword
    clean_text = re.sub("""(}[\s]*(Copyright)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@’#“!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "Copyright" keyword

    clean_text = re.sub("""(}[\s]*With News Wire Services[\s]*{)""",'}{',clean_text) #removing "With News Wire Services" keyword
    clean_text = re.sub("""(}[\s]*The Pinstripe Express[\s]*{)""",'}{',clean_text) #removing "The Pinstripe Express" keyword
    clean_text = re.sub("""(}[\s]*Weekly[\s]*{)""",'}{',clean_text) #removing "Weekly" keyword
    clean_text = re.sub("""(}[\s]*(The Daily News )+[Õa-zA-Z=".\s\d&#-;,<>:_'?|@“#!~`$’%^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "The Daily News " keyword
    clean_text = re.sub("""(}[\s]*(By submitting your email)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@#!~`$’%^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "By submitting your email" keyword
    #clean_text = re.sub("""(}[\s]*The Daily News Flash[\s]*{)""",'}{',clean_text) #removing "The Daily News Flash" keyword
    clean_text = re.sub("""(}[\s]*Weekdays[\s]*{)""",'}{',clean_text) #removing "Weekdays" keyword
    clean_text = re.sub("""(}[\s]*(Catch up on )+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@#!~`$’%^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Catch up on " keyword
    clean_text = re.sub("""(}[\s]*Breaking News[\s]*{)""",'}{',clean_text) #removing "Breaking News" keyword
    clean_text = re.sub("""(}[\s]*As it happens[\s]*{)""",'}{',clean_text) #removing "As it happens" keyword
    clean_text = re.sub("""(}[\s]*(Get updates on )+[Õa-zA-Z=".\s\d&#-;,<>:_'?|“@#!~`$’%^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Get updates on " keyword
    clean_text = re.sub("""(}[\s]*(\[)+[Õa-zA-Z=".\s\d&#-;,<>:_'?|“@#!~`$’%^&*()\-_=+\[\]]*(\])+[\s]*{)""",'}{',clean_text) #removing sentence starting with "[" and ending with "]" keywords

    clean_text = re.sub("""(}[\s]*(Never miss a story)+[Õa-zA-Z=".\s\d&#-;,<>'?|“@#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Never miss a story" keyword
    clean_text = re.sub("""({p}[\s]*[A-Z\s/.:]+{\/p})""",'',clean_text) #removing paragraph having  all caps and / and space and . AND :
    clean_text = re.sub("""(}[\s]*(Write to)+[Õa-zA-Z=".\s\d&#-;,<>'?|“@#!~`$’%—^&*()\-_=+\[\]]*)""",'}',clean_text) #removing sentence starting with "Write to" keyword
    clean_text = re.sub("""(}[\s]*(By )+[A-Za-z]*[\s]*[A-Za-z]*[\s]*[A-Za-z]{)""",'}{',clean_text) #removing sentence starting with "Write to" keyword

    clean_text = re.sub("""(}[\s]*(Follow )+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Follow " keyword
    clean_text = re.sub("""(}[\s]*(FOLLOW )+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "FOLLOW " keyword
    clean_text = re.sub("""(}[\s]*[\d]*[\s]*{)""",'}{',clean_text) #removing para with numbers only keyword
    clean_text = re.sub("""(}[\s]*(View Profile)+[Õa-zA-Z=".\s\d&“#-;,<>'?|@#!~`$’%—^&*()\-_=+\[\]]*)""",'}',clean_text) #removing sentence starting with "View Profile" keyword
    clean_text = re.sub("""((Watch :)+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""",'{',clean_text) #removing sentence starting with "Watch :" keyword
    clean_text = re.sub("""((Watch:)+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""",'{',clean_text) #removing sentence starting with "Watch:" keyword
    clean_text = re.sub("""((WATCH :)+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""",'{',clean_text) #removing sentence starting with "WATCH :" keyword
    clean_text = re.sub("""((WATCH:)+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""",'{',clean_text) #removing sentence starting with "WATCH:" keyword
    clean_text = re.sub("""(}[\s]*(Pick up )+[Õa-zA-Z=".\s\d&“#-;,<>'?|@#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Pick up " keyword
    clean_text = re.sub("""(}[\s]*(PICK UP )+[Õa-zA-Z=".\s\d&“#-;,<>'?|@#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "PICK UP " keyword

    clean_text = re.sub("""(}[\s]*(Photo)+[\s]*(:)+[Õa-zA-Z=".\s\d&“#-;,<>'?|@#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Photo :" or "Photo:" keyword
    clean_text = re.sub("""(}[\s]*(PHOTO)+[\s]*(:)+[Õa-zA-Z=".\s\d&“#-;,<>'?|@#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "PHOTO :" or "PHOTO:" keyword
    clean_text = re.sub("""(}[\s]*[A-Za-z]*[\s]*{)""",'}{',clean_text) #removin para with alphabets only keyword
    clean_text = re.sub("""(}[\s]*[Õa-zA-Z=".\s\d&#-;,'?|<>@“#!~`$’%—^&*()\-_=+\[\]]{2}[\s]*{)""",'}{',clean_text) #removin para with 2 length
    clean_text = re.sub("""(}[\s]*(Photograph by )+[Õa-zA-Z=".\s\d&“#-;,<>'?|@#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "Photograph by " keyword
    clean_text = re.sub("""(}[\s]*(PHOTOGRAPH BY )+[Õa-zA-Z=".\s\d&“#-;,<>'?|@#!~`$’%—^&*()\-_=+\[\]]*{)""",'}{',clean_text) #removing sentence starting with "PHOTOGRAPH BY " keyword
    clean_text = re.sub("""([\s]*(CLICK HERE)+[\s]*)""",'',clean_text) #removing text "CLICK HERE"
    clean_text = re.sub("""([\s]*(Click Here)+[\s]*)""",'',clean_text) #removing text "Click Here"
    clean_text = re.sub("""([\s]*(Click here)+[\s]*)""",'',clean_text) #removing text "Click here"
    clean_text = re.sub("""([\s]*(click here)+[\s]*)""",'',clean_text) #removing text "click here"

    clean_text = re.sub("""({i}[Õa-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$’“%—^&*()\-’_=+\[\]]+{/i})""",'',clean_text) #removing i-tag sentence (specifically for FOX Business)
    clean_text = re.sub("""({i}[Õa-zA-Z=".\s\d&#-;,<>:_'?|@#!~`$’“%—^&*()\-’_=+\[\]]+{i})""",'',clean_text) #removing i-tag sentence (specifically for Forbes)



    # For vulture.com
    clean_text = re.sub(r'\s*Related{/h2}\s*', "", clean_text)
    clean_text = re.sub(r'\\n+', '\\n', clean_text)

    # For usmagazine
    clean_text = re.sub(r"Subscribe to newsletters.*?{/p}\n\s*\n\s*{/p}", "", clean_text, flags=re.DOTALL) # Removing the texts starting with "Subscribe to newsletters" and ending with "{/p}\n\s*\n\s*{/p}"
    clean_text = re.sub(r'\s*{p}You have successfully subscribed.{/p}\s*', "", clean_text) # Removing the words "You have successfully subscribed"
    clean_text = re.sub("Related:.*?\.\.\.", "", clean_text) # Removing the texts starting with "Related" and ending with "\t\t{/p}\n\t\n{p}"
    clean_text = re.sub("Related:.*?\t\t{/p}\n\t\n{p}", "{p}", clean_text)
    clean_text = re.sub(r'In this article{/h3}.*?{IMG_\d+}}{/h3}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'In this article{/h3}.*?{img src={IMG_\d+}}.*?{/h3}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}See it:.*?{/strong}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}Not what .*?!{/strong}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}See it: Get the.*?{/strong}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'Related: {/p}.*?\t\t{/p}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'In this article.*?{/p}', '', clean_text, flags=re.DOTALL)

    # For einnews
    clean_text = re.sub("{p}Page Content{/p}", "", clean_text)
    clean_text = re.sub(r'{strong}Contacts:{/strong}.*?{img src={IMG_\d+}}{br}{img src={IMG_\d+}}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}Company Contacts:{/strong}.*?{img src={IMG_\d+}}{br}{img src={IMG_\d+}}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}Contact:{/strong}.*?{img src={IMG_\d+}}{br}{img src={IMG_\d+}}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'\\r', '', clean_text)
    clean_text = re.sub(r'{p}For more information, contact:{/p}.*?{/p}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'&#226;&#128;&#162;', '•', clean_text)

    # For essentiallysports
    clean_text = re.sub("""(}[\s]*(Article continues below this)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@’#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text)
    clean_text = re.sub("""(}[\s]*(America&#8217;s Favorite Video Toda)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@’#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text)
    clean_text = re.sub("""(}[\s]*(Providing feedback will help us make your experience)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@’#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text)
    clean_text = re.sub("""(}[\s]*(Enjoyed Your Read?)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@’#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text)
    clean_text = re.sub(r'{p}Least Likely{/p}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{p}Most Likely{/p}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub("""(}[\s]*(The Fan's Perspectiv)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@’#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text)


    clean_text = re.sub("""(}[\s]*(For more information)+[Õa-zA-Z=".\s\d&“#-;,<>:_'?|@’#!~`$%^&*()\-_=+\[\]]+{)""",'}{',clean_text) #removing sentence starting with "For more information" keyword

    ###############################
    # fox26houston
    clean_text = re.sub(r'{strong}PREVIOUS: {/strong}.*?{/strong}', '',  clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{p}\(KUTV-TV via FOX\) {/p}', '', clean_text)
    clean_text = re.sub(r'{p}{i}{strong}Have a finance-related question.*?{/p}', "", clean_text, flags=re.DOTALL)
    # clean_text = re.sub(r'article{/p}{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}RELATED: {/strong}{strong}.*?{/strong}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}EARLIER: {/strong}{strong}.*?{/strong}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{p}{strong}SUGGESTED: {/strong}{strong}.*?{/strong}{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'SUGGESTED:  {strong}.*?{/strong}{/p}', "",clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}FOX 26 Houston is now.*?{/strong}', "", clean_text, flags=re.DOTALL)



    # For globalnews
    clean_text = re.sub(r'{p}Send this page to someone via email{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}.*?Get the latest National news.*?{/strong}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'Story continues below advertisement{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'View image in full screen{/p}', "", clean_text, flags=re.DOTALL)

    # For cbs4local
    clean_text = re.sub(r'{strong}RECOMMENDED: {/strong}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'to receive the top interesting stories from in and around our community once daily in your inbox.', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{p}{strong}READ MORE: {/strong}{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}RECOMMENDED:{/strong}', "", clean_text, flags=re.DOTALL)

    # For fox7austin
    clean_text = re.sub(r'{p}{strong}MORE: {/strong}{strong}.*?{/strong}{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{p}{strong}READ:{/strong}{strong}.*?{/strong}{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{p}{strong}RELATED:{/strong}{strong}.*?{/strong}{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}NASA&#8217;{/strong}', "", clean_text, flags=re.DOTALL)

    # For kearneyhub
    clean_text = re.sub(r'\d+{/p} Comments.*?{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub("""(}[\s]*(Be the first to know)+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""", '}{', clean_text)
    clean_text = re.sub("""(}*[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]+(Get local news delivered to your inbox)+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""", '}{', clean_text)
    clean_text = re.sub("""(}*[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]+(I understand and agree that registration on or use of this site constitutes agreement to its user agreement and  privacy policy .)+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""", '}{', clean_text)
    clean_text = re.sub(r'Subscribe to our Daily Headlines newsletter.', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'} Obituaries Newsletter{', "}{", clean_text, flags=re.DOTALL)
    clean_text = re.sub(re.escape("* I understand and agree that registration on or use of this site constitutes agreement to its user agreement and  privacy policy ."), "", clean_text)
    clean_text = re.sub(re.escape("{/h2}\n                 .{/p}"), "", clean_text)
    clean_text = re.sub("""(}[\s]*(Get in the game with our)+[Õa-zA-Z=".\s\d&#-;,<>'?|@“#!~`$’%—^&*()\-_=+\[\]]*{)""", "}{", clean_text)
    clean_text = re.sub(r'Sent weekly directly to your inbox!', "", clean_text, flags=re.DOTALL)

    # For peoplenewspapers
    clean_text = re.sub(r'Share this article...', "", clean_text, flags=re.DOTALL)

    # For wftv.com
    clean_text = re.sub(r'{b}Read:.*?{/b}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'}to download our free news, weather and smart TV apps. Andto stream Channel 9 Eyewitness News live.{', "}{", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'&#169;2024 Cox Media Group', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'&#169; 2024 Cox Media Group', "", clean_text, flags=re.DOTALL)

    # For ksat.com
    clean_text = re.sub(r'More UIL and Big Game Coverage on KSAT:', "", clean_text, flags=re.DOTALL)

    # For nme.com
    clean_text = re.sub(r'{p}{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{/p}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'\n{p}{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{br}\n{strong}{/strong}{/p}\n', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{strong}READ MORE:.*?{/strong}', "", clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'{li}\s*{/li}', "", clean_text, flags=re.DOTALL)


    # display(clean_text)



    clean_text = re.sub('(\\n)','',clean_text) #removing new line character
    clean_text = re.sub('(\\t)','',clean_text) #removing tabular character
    clean_text = re.sub('(\\r)','',clean_text) #removing carriage return character
    clean_text = re.sub('({p}{br}{/p})','',clean_text) # removing line break
    clean_text = re.sub('({p}[\s]*{/p})','',clean_text) #removing empty p-tag keyword
    clean_text = re.sub('({strong}[\s]*{\/strong})','',clean_text) #removing empty strong-tag keyword
    clean_text = re.sub('({/a}[\s]*{/a})','',clean_text) #removing empty a-tag keyword



    clean_text = html.unescape(clean_text) #decoding unicode entities using html parser
    clean_text = replace_all1(clean_text,tags)

    # cleaning emoji
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                           "]+", flags=re.UNICODE)

    clean_text = emoji_pattern.sub(r'', clean_text)
    clean_text = unicodedata.normalize("NFKD",clean_text) #decoding utf-8 unicode data which is producing spacing

    # storing words in list with no extra spaces
    clean_text= [j for j in clean_text.strip().split(" ") if j !=""]

    return " ".join(clean_text)
