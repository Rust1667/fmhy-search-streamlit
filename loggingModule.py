import streamlit as st

import datetime
def getDateTimeString():
    now = datetime.datetime.now()
    dateTimeString = now.strftime("%Y/%m/%d-%H:%M:%S")
    return dateTimeString


import gspread

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
    file = gspread.service_account_from_dict(credentials)
    sheet = file.open("logger")
    return sheet

def logToGoogleSheet(stringToLog):
    sheet = getAuthorizedGoogleSheet()
    sheet = sheet.sheet1 #sheet inside the g-sheets document
    dataToAppend = [getDateTimeString(), stringToLog]
    sheet.append_row(dataToAppend, table_range="A1:B1")