import datetime
import pytz
import streamlit as st
def announcement():
    message = "On 2023-March-13 the app will be inaccessible from approx. 8:00-14:00 PST. ([reasons](https://discuss.streamlit.io/t/streamlit-community-cloud-downtime-on-march-13th/38828))"
    date_and_time_start = datetime.datetime(2023, 3, 12, 8, 0, 0, tzinfo=datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-8)))
    date_and_time_end = datetime.datetime(2023, 3, 13, 8, 0, 0, tzinfo=datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-8)))
    pst = pytz.timezone('US/Pacific')
    current_time = datetime.datetime.now(pst)
    if current_time < date_and_time_end and current_time > date_and_time_start:
        st.markdown(message)