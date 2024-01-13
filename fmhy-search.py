## Streamlit code
import streamlit as st

st.set_page_config(
    page_title="FMHY Search",
    page_icon="https://i.imgur.com/s9abZgP.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/Rust1667/fmhy-search-streamlit',
        'Report a bug': "https://github.com/Rust1667/fmhy-search-streamlit/issues",
        'About': "https://github.com/Rust1667/fmhy-search-streamlit"
    }
)


st.title("Search FMHY")

with st.sidebar:
    st.image("https://i.imgur.com/s9abZgP.png", width=100)
    st.text("Search Engine for r/FREEMEDIAHECKYEAH")
    st.markdown("Links:")
    st.markdown("* Wiki: [Reddit](https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/index/), [.net](https://fmhy.net/) / [.pages](https://fmhy.pages.dev/), [.tk](https://www.fmhy.tk/) / [.vercel](https://fmhy.vercel.app/), [raw](https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page)")
    st.markdown("* [Github Repo (web-app)](https://github.com/Rust1667/fmhy-search-streamlit)")
    st.markdown("* [Github Repo (script)](https://github.com/Rust1667/a-FMHY-search-engine)")
    st.markdown("* [Other Search Tools for FMHY](https://www.reddit.com/r/FREEMEDIAHECKYEAH/comments/105xraz/howto_search_fmhy/)")

queryInputFromBox = st.text_input(label=" ", value="", help="Search for links in the Wiki.")


##Config
coloring = False
#coloring = st.checkbox('Coloring', help="Many links won't work when this is active.")

printRawMarkdown = False
#printRawMarkdown = st.checkbox('Raw')

failedSearchInfoMsg = "For specific media or software, try a [CSE](https://fmhy.pages.dev/internet-tools#search-tools) / Live Sports [here](https://fmhy.pages.dev/videopiracyguide#live-tv-sports) / Ask in [Discord](https://www.reddit.com/r/FREEMEDIAHECKYEAH/comments/17f8msf/public_discord_server/)"

import requests

#----------------Alt Indexing------------
doAltIndexing = True #st.checkbox('Alt indexing', help="Includes the parent wiki page at the beginning of each result.")

def addPretext(lines, icon, baseURL, subURL):
    modified_lines = []
    currMdSubheading = ""
    currSubCat = ""
    currSubSubCat = ""

    for line in lines:
        if line.startswith("#"): #Title Lines
            if not subURL=="storage":
                if line.startswith("# ►"):
                    currMdSubheading = "#" + line.replace("# ►", "").strip().replace(" / ", "-").replace(" ", "-").lower()
                    currSubCat = "/ " + line.replace("# ►", "").strip() + " "
                    currSubSubCat = ""
                elif line.startswith("## ▷"):
                    if not subURL=="non-english": #Because non-eng section has multiple subsubcats with same names
                        currMdSubheading = "#" + line.replace("## ▷", "").strip().replace(" / ", "-").replace(" ", "-").lower()
                    currSubSubCat = "/ " + line.replace("## ▷", "").strip() + " "
            elif subURL=="storage":
                if line.startswith("## "):
                    currMdSubheading = "#" + line.replace("## ", "").strip().replace(" / ", "-").replace(" ", "-").lower()
                    currSubCat = "/ " + line.replace("## ", "").strip() + " "
                    currSubSubCat = ""
                elif line.startswith("### "):
                    currMdSubheading = "#" + line.replace("### ", "").strip().replace(" / ", "-").replace(" ", "-").lower()
                    currSubSubCat = "/ " + line.replace("### ", "").strip() + " "

            # Remove links from subcategory titles (because the screw the format)
            if 'http' in currSubCat: currSubCat = ''
            if 'http' in currSubSubCat: currSubSubCat = ''

        elif any(char.isalpha() for char in line): #If line has content
            preText = f"[{icon}{currSubCat}{currSubSubCat}]({baseURL}{subURL}{currMdSubheading}) ► "
            if line.startswith("* "): line = line[2:]
            modified_lines.append(preText + line)

    return modified_lines

#----------------base64 page processing------------
import base64
import re

doBase64Decoding = True

def fix_base64_string(encoded_string):
    missing_padding = len(encoded_string) % 4
    if missing_padding != 0:
        encoded_string += '=' * (4 - missing_padding)
    return encoded_string

def decode_base64_in_backticks(input_string):
    def base64_decode(match):
        encoded_data = match.group(0)[1:-1]  # Extract content within backticks
        decoded_bytes = base64.b64decode( fix_base64_string(encoded_data) )
        return decoded_bytes.decode()

    pattern = r"`[^`]+`"  # Regex pattern to find substrings within backticks
    decoded_string = re.sub(pattern, base64_decode, input_string)
    return decoded_string

def remove_empty_lines(text):
    lines = text.split('\n')  # Split the text into lines
    non_empty_lines = [line for line in lines if line.strip()]  # Filter out empty lines
    return '\n'.join(non_empty_lines)  # Join non-empty lines back together

def extract_base64_sections(base64_page):
    sections = base64_page.split("***")  # Split the input string by "***" to get sections
    formatted_sections = []
    for section in sections:
        formatted_section = remove_empty_lines( section.strip().replace("#### ", "").replace("\n\n", " - ").replace("\n", ", ") )
        if doBase64Decoding: formatted_section = decode_base64_in_backticks(formatted_section)
        formatted_section = '[🔑Base64](https://rentry.co/FMHYBase64) ► ' + formatted_section
        formatted_sections.append(formatted_section)
    lines = formatted_sections
    return lines
#----------------</end>base64 page processing------------


def dlWikiChunk(fileName, icon, redditSubURL):

    #download the chunk
    if not fileName=='base64.md':
        print("Downloading " + fileName + "...")
        page = requests.get("https://raw.githubusercontent.com/nbats/FMHYedit/main/" + fileName).text
    elif fileName=='base64.md':
        print("Downloading rentry.co/FMHYBase64...")
        page = requests.get("https://rentry.co/FMHYBase64/raw").text.replace("\r", "")
    print("Downloaded")

    #add a pretext
    redditBaseURL = "https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/"
    pagesDevSiteBaseURL = "https://fmhy.pages.dev/"
    baseURL = pagesDevSiteBaseURL
    if not fileName=='base64.md':
        pagesDevSiteSubURL = fileName.replace(".md", "").lower()
        subURL = pagesDevSiteSubURL
        lines = page.split('\n')
        lines = addPretext(lines, icon, baseURL, subURL)
    elif fileName=='base64.md':
        lines = extract_base64_sections(page)

    return lines

def cleanLineForSearchMatchChecks(line):
    return line.replace('https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/', '/').replace('https://fmhy.pages.dev/', '/')

@st.cache_resource(ttl=43200)
def alternativeWikiIndexing():
    wikiChunks = [
        dlWikiChunk("VideoPiracyGuide.md", "📺", "video"),
        dlWikiChunk("AI.md", "🤖", "ai"),
        dlWikiChunk("Android-iOSGuide.md", "📱", "android"),
        dlWikiChunk("AudioPiracyGuide.md", "🎵", "audio"),
        dlWikiChunk("DownloadPiracyGuide.md", "💾", "download"),
        dlWikiChunk("EDUPiracyGuide.md", "🧠", "edu"),
        dlWikiChunk("GamingPiracyGuide.md", "🎮", "games"),
        dlWikiChunk("AdblockVPNGuide.md", "📛", "adblock-vpn-privacy"),
        dlWikiChunk("System-Tools.md", "💻", "system-tools"),
        dlWikiChunk("File-Tools.md", "🗃️", "file-tools"),
        dlWikiChunk("Internet-Tools.md", "🔗", "internet-tools"),
        dlWikiChunk("Social-Media-Tools.md", "💬", "social-media"),
        dlWikiChunk("Text-Tools.md", "📝", "text-tools"),
        dlWikiChunk("Video-Tools.md", "📼", "video-tools"),
        dlWikiChunk("MISCGuide.md", "📂", "misc"),
        dlWikiChunk("ReadingPiracyGuide.md", "📗", "reading"),
        dlWikiChunk("TorrentPiracyGuide.md", "🌀", "torrent"),
        dlWikiChunk("img-tools.md", "📷", "img-tools"),
        dlWikiChunk("LinuxGuide.md", "🐧🍏", "linux"),
        dlWikiChunk("DEVTools.md", "🖥️", "dev-tools"),
        dlWikiChunk("Non-English.md", "🌏", "non-eng"),
        dlWikiChunk("STORAGE.md", "🗄️", "storage"),
        dlWikiChunk("base64.md", "🔑", "base64"),
        dlWikiChunk("NSFWPiracy.md", "🌶", "https://saidit.net/s/freemediafuckyeah/wiki/index")
    ]
    return [item for sublist in wikiChunks for item in sublist] #Flatten a <list of lists of strings> into a <list of strings>
#--------------------------------

def getAllLines():
    #if doAltIndexing:
    return alternativeWikiIndexing()

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
    searchInput = searchInput.strip()

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

    #print search results count
    if len(linesFound)>0:
        st.text(str(len(linesFound)) + " search results for " + searchInput + ":\n")
    else:
        st.markdown("No results found for " + searchInput + "!")
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
    if len(linesFound)>0 and len(linesFound)<=10:
        with st.expander("Not what you were looking for?"):
            st.info(failedSearchInfoMsg, icon="ℹ️")


## Execute at start of script
lineList = getAllLines()


## Streamlit code
def put_query_in_URL(queryInput):
    queryStringInURL = queryInput.strip()
    if not queryStringInURL=="":
        st.experimental_set_query_params(
            q=queryStringInURL
        )
    else:
        st.experimental_set_query_params()

def search_from_URL_query():
    queryParameters = st.experimental_get_query_params()
    if "q" in queryParameters:
        queryWords = queryParameters['q']
        queryInput = " ".join(queryWords)
        doASearch(queryInput)

if st.button("Search"):
    queryInput = queryInputFromBox
    doASearch(queryInput)
    put_query_in_URL(queryInput)
else:
    search_from_URL_query()
