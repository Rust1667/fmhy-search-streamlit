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

import dateTimeBasedAnnouncement
dateTimeBasedAnnouncement.announcement()

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

failedSearchInfoMsg = "For specific media or software, try a [CSE](https://github.com/nbats/FMHY/wiki/%F0%9F%94%A7-Tools#-search-tools) / Live Sports [here](https://github.com/nbats/FMHY/wiki/%F0%9F%93%BA-Movies---TV---Anime---Sports#-live-tv--sports) / Ask in [Divolt](https://fmhy.divolt.xyz/)"

import requests
import loggingModule

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

def cleanLineForSearchMatchChecks(line):
    return line.replace('https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/', '/')

@st.cache_resource(ttl=86400)
def alternativeWikiIndexing():
    wikiChunks = [
        dlWikiChunk("VideoPiracyGuide.md", "📺", "video"),
        dlWikiChunk("Android-iOSGuide.md", "📱", "android"),
        dlWikiChunk("AudioPiracyGuide.md", "🎵", "audio"),
        dlWikiChunk("DownloadPiracyGuide.md", "💾", "download"),
        dlWikiChunk("EDUPiracyGuide.md", "🧠", "edu"),
        dlWikiChunk("GamingPiracyGuide.md", "🎮", "games"),
        dlWikiChunk("Game-Tools.md", "🎮🔧", "game-tools"),
        dlWikiChunk("AdblockVPNGuide.md", "📛", "adblock-vpn-privacy"),
        dlWikiChunk("TOOLSGuide.md", "🔧", "tools-misc"),
        dlWikiChunk("MISCGuide.md", "📂", "misc"),
        dlWikiChunk("ReadingPiracyGuide.md", "📗", "reading"),
        dlWikiChunk("TorrentPiracyGuide.md", "🌀", "torrent"),
        dlWikiChunk("img-tools.md", "🖼️🔧", "img-tools"),
        dlWikiChunk("LinuxGuide.md", "🐧🍏", "linux"),
        dlWikiChunk("DEVTools.md", "🖥️", "dev-tools"),
        dlWikiChunk("Non-English.md", "🌏", "non-eng"),
        dlWikiChunk("STORAGE.md", "🗄️", "storage"),
        dlWikiChunk("NSFWPiracy.md", "🌶", "https://saidit.net/s/freemediafuckyeah/wiki/index")
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

def removeEmptyStringsFromList(stringList):
    return [string for string in stringList if string != '']

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
    lineWords = removeEmptyStringsFromList( line.lower().replace('[', ' ').replace(']', ' ').split(' ') )
    lineWords = [element.strip() for element in lineWords] #doesnt work on streamlit without this line even though it works locally
    searchQueryWords = removeEmptyStringsFromList( searchQuery.lower().split(' ') )
    return checkList1isInList2(searchQueryWords, lineWords)

def moveBetterMatchesToFront(myList, searchQuery):
    bumped = []
    notBumped = []
    for element in myList:
        if checkWordForWordMatch(element, searchQuery):
            bumped.append(element)
        else:
            notBumped.append(element)
    return (bumped + notBumped)

def getOnlyFullWordMatches(myList, searchQuery):
    bumped = []
    for element in myList:
        if checkWordForWordMatch(element, searchQuery):
            bumped.append(element)
    return bumped

def getLinesThatContainAllWords(lineList, searchQuery):
    words = removeEmptyStringsFromList( searchQuery.lower().split(' ') )
    bumped = []
    for line in lineList:
        if doAltIndexing:
            lineModdedForChecking = cleanLineForSearchMatchChecks(line).lower()
        else:
            lineModdedForChecking = line.lower()
        for word in words:
            if word not in lineModdedForChecking:
                break
        else:
            bumped.append(line)
    return bumped

def filterLines(lineList, searchQuery):
    if len(searchQuery)<=2 or (searchQuery==searchQuery.upper() and len(searchQuery)<=5):
        return getOnlyFullWordMatches(lineList, searchQuery)
    else:
        return getLinesThatContainAllWords(lineList, searchQuery)

def filterOutTitleLines(lineList):
    filteredList = []
    sectionTitleList = []
    for line in lineList:
        if line[0] != "#":
            filteredList.append(line)
        else:
            sectionTitleList.append(line)
    return [filteredList, sectionTitleList]



def doASearch(searchInput):

    #make sure the input is right before continuing
    if searchInput=="":
        st.warning("The search query is empty.", icon="⚠️")
        return
    #if len(searchInput)<2 and not searchInput=="⭐":
    #    st.warning("The search query is too short.", icon="⚠️")
    #    return

    #main results
    myLineList = lineList
    linesFoundPrev = filterLines(myLineList, searchInput)

    #show only full word matches if there are too many results
    if len(linesFoundPrev) > 300:
        toomanywarningmsg = "Too many results (" + str(len(linesFoundPrev)) + "). " + "Showing only full-word matches."
        st.text(toomanywarningmsg)
        linesFoundPrev = getOnlyFullWordMatches(linesFoundPrev, searchInput)

    #rank results
    #linesFoundPrev = moveExactMatchesToFront(linesFoundPrev, searchInput)
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
    textToPrint = "\n\n".join(linesFound)

    #check for porn words
    pornWords = ['nsfw', 'porn', 'onlyfans', 'xxx', 'hentai', 'sex']
    thereArePornWords = any(word in pornWords for word in myFilterWords)

    if searchInput.lower() == 'porn':
        st.info("The full NSFW Wiki Section is [here](https://saidit.net/s/freemediafuckyeah/wiki/index).", icon="ℹ️")

    #print search results count
    if len(linesFound)>0:
        st.text(str(len(linesFound)) + " search results:\n")
    else:
        st.markdown("No results found!")
        if not thereArePornWords:
            st.info(failedSearchInfoMsg, icon="ℹ️")

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

    #Some results but maybe not enough
    if len(linesFound)>0 and len(linesFound)<=10 and not thereArePornWords:
        with st.expander("Not what you were looking for?"):
            st.info(failedSearchInfoMsg, icon="ℹ️")

    #full nsfw section in case people look for it
    if thereArePornWords and len(linesFound)==0:
        st.info("The full NSFW Wiki Section is [here](https://saidit.net/s/freemediafuckyeah/wiki/index).", icon="ℹ️")



## Execute at start of script
lineList = getAllLines()


## Streamlit code
if st.button("Search"):
    doASearch(queryInput.strip())

    #logging
    print("searching: " + queryInput)
    try:
        loggingModule.logToGoogleSheet(queryInput)
    except:
        print("Google sheet error.")