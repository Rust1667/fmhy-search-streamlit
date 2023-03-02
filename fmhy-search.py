## Streamlit code
import streamlit as st

st.set_page_config(
    page_title="FMHY Search",
    page_icon="https://i.imgur.com/s9abZgP.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/Rust1667/a-FMHY-search-engine',
        'Report a bug': "https://github.com/Rust1667/a-FMHY-search-engine",
        'About': "https://github.com/Rust1667/a-FMHY-search-engine"
    }
)

st.title("Search FMHY")

with st.sidebar:
    st.image("https://i.imgur.com/s9abZgP.png", width=100)
    st.text("Search Engine for r/FREEMEDIAHECKYEAH")
    st.markdown("Links:")
    st.markdown("[Wiki on Reddit](https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/index/)")
    st.markdown("[Wiki as Raw Markdown](https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page)")
    #st.markdown("[Github Repository for this tool (web-app)](https://github.com/Rust1667/fmhy-search-streamlit)")
    st.markdown("[Github Repository for this tool (script version)](https://github.com/Rust1667/a-FMHY-search-engine)")
    st.markdown("[Other Search Tools for FMHY](https://www.reddit.com/r/FREEMEDIAHECKYEAH/comments/105xraz/howto_search_fmhy/)")

queryInput = st.text_input(label=" ", value="", help="Search for links in the Wiki.")


##Config
coloring = False 
#coloring = st.checkbox('Coloring', help="Many links won't work when this is active.")

printRawMarkdown = False 
#printRawMarkdown = st.checkbox('Raw')

import requests


#----------------Alt Indexing------------
doAltIndexing = True #st.checkbox('Alt indexing', help="Includes the parent wiki page at the beginning of each result.")

def addPretext(lines, preText):
    for i in range(len(lines)):
        lines[i] = preText + lines[i]
    return lines

def dlWikiChunk(fileName, icon, subURL):
    #download the chunk
    print("Downloading " + fileName + "...")
    lines = requests.get("https://raw.githubusercontent.com/nbats/FMHYedit/main/" + fileName).text.split('\n')
    print("Downloaded")

    #add a pretext
    if not fileName=="NSFWPiracy.md":
        preText = "[" + icon + "](" + "https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/" + subURL + ") "
    else:
        preText = "[" + icon + "](" + subURL + ") "
    lines = addPretext(lines, preText)
    
    return lines

@st.cache_resource(ttl=86400)
def alternativeWikiIndexing():
    wikiChunks = [
        dlWikiChunk("AdblockVPNGuide.md", "📛", "adblock-vpn-privacy"),
        dlWikiChunk("AndroidPiracyGuide.md", "📱", "android"),
        dlWikiChunk("AudioPiracyGuide.md", "🎵", "audio"),
        dlWikiChunk("DEVTools.md", "🖥️", "dev-tools"),
        dlWikiChunk("DownloadPiracyGuide.md", "💾", "download"),
        dlWikiChunk("EDUPiracyGuide.md", "🧠", "edu"),
        dlWikiChunk("Game-Tools.md", "🎮🔧", "game-tools"),
        dlWikiChunk("GamingPiracyGuide.md", "🎮", "games"),
        dlWikiChunk("LinuxGuide.md", "🐧🍏", "linux"),
        dlWikiChunk("MISCGuide.md", "📂", "misc"),
        dlWikiChunk("NSFWPiracy.md", "🌶", "https://saidit.net/s/freemediafuckyeah/wiki/index"),
        dlWikiChunk("Non-English.md", "🌏", "non-eng"),
        dlWikiChunk("ReadingPiracyGuide.md", "📗", "reading"),
        dlWikiChunk("STORAGE.md", "🗄️", "storage"),
        dlWikiChunk("TOOLSGuide.md", "🔧", "tools-misc"),
        dlWikiChunk("TorrentPiracyGuide.md", "🌀", "torrent"),
        dlWikiChunk("VideoPiracyGuide.md", "📺", "video"),
        dlWikiChunk("img-tools.md", "🖼️🔧", "img-tools")
    ]
    return [item for sublist in wikiChunks for item in sublist]
#--------------------------------

@st.cache_resource(ttl=86400)
def standardWikiIndexing():
    try:
        #First, try to get it from Github
        response1 = requests.get("https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page")
        data = response1.text
    except:
        #If that fails, get it from the local backup
        with open('single-page', 'r') as f:
            data = f.read()
    lines = data.split('\n')
    return lines


def getAllLines():
    if doAltIndexing:
        try:
            lines = alternativeWikiIndexing()
        except:
            lines = standardWikiIndexing()
    else:
        lines = standardWikiIndexing()
    return lines


import datetime
def getDateTimeString():
    now = datetime.datetime.now()
    dateTimeString = now.strftime("%Y/%m/%d-%H:%M:%S")
    return dateTimeString


from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json

@st.cache_resource(ttl=86400)
def getAuthorizedGoogleSheet():
    credentials = {
      "type": st.secrets.type,
      "project_id": st.secrets.project_id,
      "private_key_id": st.secrets.private_key_id,
      "private_key": st.secrets.private_key,
      "client_email": st.secrets.client_email,
      "client_id": st.secrets.client_id,
      "auth_uri": st.secrets.auth_uri,
      "token_uri": st.secrets.token_uri,
      "auth_provider_x509_cert_url": st.secrets.auth_provider_x509_cert_url,
      "client_x509_cert_url": st.secrets.client_x509_cert_url
    }
    scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
    ]
    file = gspread.service_account_from_dict(credentials)
    sheet = file.open("logger")
    return sheet

def logToGoogleSheet(stringToLog):
    sheet = getAuthorizedGoogleSheet()
    sheet = sheet.sheet1 #sheet inside the g-sheets document
    dataToAppend = [getDateTimeString(), stringToLog]
    sheet.append_row(dataToAppend, table_range="A1:B1")



def checkMultiWordQueryContainedExactlyInLine(line, searchQuery):
    if len(searchQuery.split(' ')) <= 1: 
        return False
    return (searchQuery.lower() in line.lower())

def moveExactMatchesToFront(myList, searchQuery):
    bumped = []
    notBumped = []
    for i in range(len(myList)):
        if checkMultiWordQueryContainedExactlyInLine(myList[i], searchQuery):
            bumped.append(myList[i])
        else:
            notBumped.append(myList[i])
    return (bumped + notBumped)

def checkList1isInList2(list1, list2):
    for element in list1:
        if element not in list2:
            return False
    return True

def checkWordForWordMatch(line, searchQuery):
    lineWords = line.lower().replace('[', ' ').replace(']', ' ').split(' ')
    searchQueryWords = searchQuery.lower().split(' ')
    return checkList1isInList2(searchQueryWords, lineWords)

def moveBetterMatchesToFront(myList, searchQuery):
    bumped = []
    notBumped = []
    for i in range(len(myList)):
        if checkWordForWordMatch(myList[i], searchQuery):
            bumped.append(myList[i])
        else:
            notBumped.append(myList[i])
    return (bumped + notBumped)

def getOnlyFullWordMatches(myList, searchQuery):
    bumped = []
    for i in range(len(myList)):
        if checkWordForWordMatch(myList[i], searchQuery):
            bumped.append(myList[i])
    return bumped

def getLinesThatContainAllWords(lineList, filterWords):
    lineListFiltered = [line for line in lineList if all(
        word.lower() in line.lower() for word in filterWords
    )]
    return lineListFiltered

def filterLines(lineList, searchQuery):
    filterWords = searchQuery.lower().split(' ')
    lineListFiltered = getLinesThatContainAllWords(lineList, filterWords)
    return lineListFiltered

def filterOutTitleLines(lineList):
    filteredList = []
    sectionTitleList = []
    for line in lineList:
        if line[0] != "#":
            filteredList.append(line)
        else:
            sectionTitleList.append(line)
    return [filteredList, sectionTitleList]

def removeHashtags(string):
    return string.replace("#", "")

def colored(word, color):
    return ":" + color + "[" + word + "]"

def highlightWord(sentence, word):
    return sentence.replace(word, colored(word,'red'))

def colorLinesFound(linesFound, filterWords):
    coloredLinesList = []
    filterWordsCapitalizedToo=[]
    for word in filterWords:
        filterWordsCapitalizedToo.append(word.capitalize())
    filterWordsCapitalizedToo.extend(filterWords)
    for line in linesFound:
        for word in filterWordsCapitalizedToo:
            line = highlightWord(line, word)
        coloredLine = line
        coloredLinesList.append(coloredLine)
    return coloredLinesList


def doASearch(searchInput):

    #make sure the input is right before continuing
    if searchInput=="":
        st.warning("The search query is empty.", icon="⚠️")
        return
    if len(searchInput)<2 and not searchInput=="⭐":
        st.warning("The search query is too short.", icon="⚠️")
        return

    #main results
    myLineList = lineList
    linesFoundPrev = filterLines(myLineList, searchInput)

    #show only full word matches if there are too many results
    if len(linesFoundPrev) > 200:
        toomanywarningmsg = "Too many results (" + str(len(linesFoundPrev)) + "). " + "Showing only full-word matches."
        st.text(toomanywarningmsg)
        linesFoundPrev = getOnlyFullWordMatches(linesFoundPrev, searchInput)

    #rank results
    linesFoundPrev = moveExactMatchesToFront(linesFoundPrev, searchInput)
    linesFoundPrev = moveBetterMatchesToFront(linesFoundPrev, searchInput)

    #extract titles lines
    linesFoundAll = filterOutTitleLines(linesFoundPrev)
    linesFound = linesFoundAll[0]
    sectionTitleList = linesFoundAll[1]

    #make sure results are not too many before continuing
    if len(linesFound) > 700 and not searchInput=="⭐":
        toomanywarningmsg = "Too many results (" + str(len(linesFound)) + ")."
        st.warning(toomanywarningmsg, icon="⚠️")

        #Print the section titles
        if len(sectionTitleList)>0:
            st.markdown(" ")
            st.markdown("There are these section titles in the Wiki: ")
            sectionTitleListToPrint = "\n\n".join(sectionTitleList)
            st.code(sectionTitleListToPrint, language="markdown")
            #st.markdown(" ")
            st.markdown("Find them by doing <Ctrl+F> in the [Raw markdown](https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page).")

        return

    myFilterWords = searchInput.lower().split(' ')

    #create string of text to print
    if coloring and not printRawMarkdown:
        linesFoundColored = colorLinesFound(linesFound, myFilterWords)
        textToPrint = "\n\n".join(linesFoundColored)
    else:
        textToPrint = "\n\n".join(linesFound)

    #check for porn words
    pornWords = ['nsfw', 'porn', 'onlyfans', 'xxx', 'hentai', 'sex']
    thereArePornWords = any(word in pornWords for word in myFilterWords)

    if searchInput=='porn':
        st.info("The full NSFW Wiki Section is [here](https://saidit.net/s/freemediafuckyeah/wiki/index).", icon="ℹ️")

    #print search results count
    if len(linesFound)>0:
        st.text(str(len(linesFound)) + " search results:\n")
    else:
        st.markdown("No results found!")
        if not thereArePornWords:
            st.info("If looking for specific media or software, try with a [CSE](https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/tools-misc#wiki_.25B7_search_tools). For Live Sports go [here](https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/video/#wiki_.25B7_live_tv_.2F_sports).", icon="ℹ️")

    # print search results
    if not printRawMarkdown:
        st.markdown(textToPrint)
    else:
        st.code(textToPrint, language="markdown")

    #title section results
    if len(sectionTitleList)>0:
        st.markdown(" ")
        st.markdown("Also there are these section titles in the Wiki: ")
        sectionTitleListToPrint = "\n\n".join(sectionTitleList)
        st.code(sectionTitleListToPrint, language="markdown")
        #st.markdown(" ")
        st.markdown("Find them by doing <Ctrl+F> in the [Raw markdown](https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page).")

    #full nsfw section in case people look for it
    if thereArePornWords:
        st.info("The full NSFW Wiki Section is [here](https://saidit.net/s/freemediafuckyeah/wiki/index).", icon="ℹ️")



## Execute at start of script
lineList = getAllLines()


## Streamlit code
if st.button("Search"):
    doASearch(queryInput)

    #logging
    print("searching: " + queryInput)
    try:
        logToGoogleSheet(queryInput)
    except:
        print("Google sheet error.")