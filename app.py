import streamlit as st
import pandas as pd

st.set_page_config(page_title="한진철관 사양조회", layout="wide")

@st.cache_data
def load_data():
    try:
        # 이 폴더 안에 '고객 사양서.xlsx' 파일이 있어야 합니다.
        df = pd.read_excel("고객 사양서.xlsx")
        return df.fillna("-")
    except Exception as e:
        st.error(f"엑셀 파일을 찾을 수 없습니다: {e}")
        return None

st.title("📱 한진철관 실시간 사양 조회")

df = load_data()

if df is not None:
    names = df.iloc[:, 0].unique()
    selected = st.selectbox("고객사를 선택하세요", names)
    data = df[df.iloc[:, 0] == selected].iloc[0]
    
    st.divider()
    for col, val in data.items():
        c1, c2 = st.columns([1, 2])
        with c1:
            st.info(f"**{col}**")
        with c2:
            if "특이" in col or "주의" in col:
                st.subheader(f":red[{val}]")
            else:
                st.subheader(val)