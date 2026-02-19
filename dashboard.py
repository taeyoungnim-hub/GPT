import requests
import streamlit as st
import pandas as pd

API_BASE = st.sidebar.text_input("API 주소", "http://127.0.0.1:8000")

st.title("부동산 공공고시 통합 대시보드")

if st.button("전체 소스 동기화"):
    res = requests.post(f"{API_BASE}/sync", timeout=120)
    if res.ok:
        st.success("동기화 완료")
        st.json(res.json())
    else:
        st.error(res.text)

keyword = st.text_input("키워드", "도시관리계획")
region = st.text_input("지역", "서울")

if st.button("문서 검색"):
    params = {"keyword": keyword, "region": region, "limit": 200}
    res = requests.get(f"{API_BASE}/documents", params=params, timeout=60)
    if not res.ok:
        st.error(res.text)
    else:
        docs = res.json()
        df = pd.DataFrame(docs)
        st.dataframe(df, use_container_width=True)

        if not df.empty:
            selected_id = int(st.selectbox("검증할 문서 ID", df["id"].tolist()))
            if st.button("검증 스코어 계산"):
                v = requests.post(f"{API_BASE}/validate/{selected_id}", timeout=30)
                if v.ok:
                    st.json(v.json())
                else:
                    st.error(v.text)
