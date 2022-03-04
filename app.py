import streamlit as st
from wc import download_report

from datetime import datetime

st.title('Download Woocommerce Report')

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

if st.button('Download',key="download"):
    csv = None
    with st.spinner('Fetching your report ...'):
        report = download_report()
        csv = convert_df(report)
    
    st.success('Report ready!')
    if csv is not None:
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'report_{datetime.utcnow()}.csv',
            mime='text/csv',
        )
