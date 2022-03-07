import streamlit as st
from wc import download_report
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta  # to add days or years

st.title("Download Woocommerce Report")


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode("utf-8")


## Range selector
cols1, cols2 = st.columns(([1, 1]))  # To make it narrower
start = cols1.date_input("Resources published after")
end = cols2.date_input("Resources published before")


if st.button("Download", key="download"):
    csv = None
    with st.spinner("Fetching your report ..."):
        start, end = dt.datetime(*start.timetuple()[:-4]).strftime(
            "%Y-%m-%dT%H:%M:%S"
        ), dt.datetime(*end.timetuple()[:-4]).strftime("%Y-%m-%dT%H:%M:%S")
        report = download_report(start, end)
        if report is None:
            st.info("No Data Available")
        else:
            csv = convert_df(report)

    if csv is not None:
        st.success("Report ready!")
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"report_{dt.datetime.utcnow()}.csv",
            mime="text/csv",
        )
