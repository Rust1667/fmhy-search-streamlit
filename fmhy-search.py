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
    st.markdown("[Wiki on Reddit](https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/index/)")
    st.markdown("[Wiki as Raw Markdown](https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page)")
    #st.markdown("[Github Repository for this tool (web-app)](https://github.com/Rust1667/fmhy-search-streamlit)")
    st.markdown("[Github Repository for this tool (script version)](https://github.com/Rust1667/a-FMHY-search-engine)")
    st.markdown("[Other Search Tools for FMHY](https://www.reddit.com/r/FREEMEDIAHECKYEAH/comments/105xraz/howto_search_fmhy/)")


##Config
coloring = False 
#coloring = st.checkbox('Coloring', help="Many links won't work when this is active.")

printRawMarkdown = False 
#printRawMarkdown = st.checkbox('Raw')

## Original script code mostly
import requests

def splitSentenceIntoWords(searchInput):
    searchInput = searchInput.lower()
    searchWords = searchInput.split(' ')
    return searchWords

@st.cache_resource(ttl=86400)
def getAllLines():
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



def filterLines(lineList, filterWords):
    sentences = lineList
    words = filterWords
    sentence = [sentence for sentence in sentences if all(
        w.lower() in sentence.lower() for w in words
    )]
    return sentence

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

    #intro to the search results
    myFilterWords = splitSentenceIntoWords(searchInput)

    print("searching: " + searchInput)

    #main results
    myLineList = lineList
    linesFoundPrev = filterLines(lineList=myLineList, filterWords=myFilterWords)
    linesFoundAll = filterOutTitleLines(linesFoundPrev)
    linesFound = linesFoundAll[0]
    sectionTitleList = linesFoundAll[1]

    #make sure results are not too many before continuing
    if len(linesFound) > 700 and not searchInput=="⭐":
        toomanywarningmsg = "Too many results. (" + str(len(linesFound)) + ")"
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

    #create string of text to print
    if coloring and not printRawMarkdown:
        linesFoundColored = colorLinesFound(linesFound, myFilterWords)
        textToPrint = "\n\n".join(linesFoundColored)
    else:
        textToPrint = "\n\n".join(linesFound)

    #check for porn words
    pornWords = ['nsfw', 'porn', 'onlyfans', 'xxx', 'hentai', 'sex']
    thereArePornWords = any(word in pornWords for word in myFilterWords)

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

def searchInputCallback():
    queryInput = st.session_state.text_input_key
    doASearch(queryInput)
    try:
        logToGoogleSheet(queryInput)
    except:
        print("Google sheet error.")


## Streamlit code
queryInput = st.text_input(label=" ", value="", help="Search for links in the Wiki.", on_change=searchInputCallback, key='text_input_key')

if st.button("Search"):
    doASearch(queryInput)

    try:
        logToGoogleSheet(queryInput)
    except:
        print("Google sheet error.")

