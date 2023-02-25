## Streamlit
import streamlit as st

st.set_page_config(
    page_title="FMHY Search",
    page_icon="https://i.imgur.com/s9abZgP.png",
    layout="centered",
    initial_sidebar_state="auto",
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


## Original script
import requests


def splitSentenceIntoWords(searchInput):
    searchInput = searchInput.lower()
    searchWords = searchInput.split(' ')
    return searchWords

def getAllLines():
    #print("Loading FMHY single-page file from Github...")
    response1 = requests.get("https://raw.githubusercontent.com/nbats/FMHYedit/main/single-page")
    #print("Loaded.\n")

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




lineList = getAllLines()




def doASearch():

    searchInput = queryInput

    #make sure the input is right before continuing
    if len(searchInput) < 2:
        st.text("The search query is too short.")
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
        st.text("Too many results.")
        return

    textToPrint = "\n\n".join(linesFound)
    st.text(str(len(linesFound)) + " search results:\n")
    st.markdown(textToPrint)

    #title section results
    if len(sectionTitleList)>0:
        st.text("Also there are these section titles: ")
        st.text("\n".join(sectionTitleList))


## Streamlit
if(st.button("Search")):
    queryInput = queryInput.title()
    doASearch()
