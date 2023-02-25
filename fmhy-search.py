## Streamlit code
import streamlit as st

st.set_page_config(
    page_title="FMHY Search",
    page_icon="https://i.imgur.com/s9abZgP.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/Rust1667/fmhy-search-streamlit',
        'Report a bug': "https://github.com/Rust1667/fmhy-search-streamlit",
        'About': "https://github.com/Rust1667/a-FMHY-search-engine"
    }
)

st.title("Search FMHY")

with st.sidebar:
    st.image("https://i.imgur.com/s9abZgP.png", width=100)
    st.markdown("[Wiki on Reddit](https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/index/)")
    st.markdown("[Wiki as Raw Markdown](https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page)")
    st.markdown("[Github Repository for this tool (web-app)](https://github.com/Rust1667/fmhy-search-streamlit)")
    st.markdown("[Github Repository for this tool (script version)](https://github.com/Rust1667/a-FMHY-search-engine)")
    st.markdown("[Other Search Tools for FMHY](https://www.reddit.com/r/FREEMEDIAHECKYEAH/comments/105xraz/howto_search_fmhy/)")

queryInput = st.text_input(label=" ", value="")

##Config
coloring = False #coloring = st.checkbox('Coloring', help="Many links won't work when this is active.")
printRawMarkdown = False #printRawMarkdown = st.checkbox('Raw') #

## Original script code mostly
import requests

def splitSentenceIntoWords(searchInput):
    searchInput = searchInput.lower()
    searchWords = searchInput.split(' ')
    return searchWords

def getAllLines():
    print("Downloading wiki from GitHub...")
    with st.spinner('Downloading wiki from GitHub...'):
        response1 = requests.get("https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page")
    print("Loaded.\n")

    data = response1.text
    lines = data.split('\n')
    return lines

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


def doASearch():

    searchInput = queryInput

    #make sure the input is right before continuing
    if searchInput == "":
        st.warning("The search query is empty.", icon="⚠️")
        return
    if len(searchInput) < 2:
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
    if len(linesFound) > 1000:
        toomanywarningmsg = "Too many results. (" + len(linesFound) + ")"
        st.warning(toomanywarningmsg, icon="⚠️")
        return

    if coloring and not printRawMarkdown:
        linesFoundColored = colorLinesFound(linesFound, myFilterWords)
        textToPrint = "\n\n".join(linesFoundColored)
    else:
        textToPrint = "\n\n".join(linesFound)

    st.text(str(len(linesFound)) + " search results:\n")

    if not printRawMarkdown:
        st.markdown(textToPrint)
    else:
        #linesFoundColored = colorLinesFound(linesFound, myFilterWords)
        #textToPrint = "\n\n".join(linesFoundColored)
        #textToPrint = textToPrint.replace("("," ").replace(")"," ")
        st.text(textToPrint)

    #title section results
    if len(sectionTitleList)>0:
        st.text("Also there are these section titles: ")
        st.text("\n".join(sectionTitleList))


## Execute at start of script
lineList = getAllLines()


## Streamlit code
if(st.button("Search")):
    queryInput = queryInput.title()
    doASearch()
