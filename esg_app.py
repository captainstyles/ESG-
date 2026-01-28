import streamlit as st
import pandas as pd
import random

# 設定網頁標題
st.set_page_config(page_title="ESG 永續發展題庫練習", layout="wide")

def load_data():
    try:
        # 讀取 CSV，指定分隔符號為 |
        df = pd.read_csv('exam_data.csv', sep='|', encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"讀取題庫失敗，請檢查 exam_data.csv 格式。錯誤訊息: {e}")
        return None

df = load_data()

if df is not None:
    st.title("🌱 ESG 永續發展基礎能力測驗")
    
    # 側邊欄設定
    st.sidebar.header("功能選單")
    mode = st.sidebar.radio("選擇模式", ["分段練習", "隨機挑戰 (80題)"])
    
    total_q = len(df)
    chunk_size = 100
    
    if mode == "分段練習":
        # 自動根據題數生成級距，如 1-100, 101-200...
        ranges = [f"{i+1} - {min(i+chunk_size, total_q)}" for i in range(0, total_q, chunk_size)]
        selected_range = st.sidebar.selectbox("選擇題目範圍", ranges)
        
        start_idx = int(selected_range.split(" - ")[0]) - 1
        end_idx = int(selected_range.split(" - ")[1])
        exam_df = df.iloc[start_idx:end_idx].copy()
    else:
        # 隨機抽 80 題
        exam_df = df.sample(n=min(80, total_q)).copy()
    
    # 練習介面
    with st.form("exam_form"):
        user_answers = {}
        for idx, row in exam_df.iterrows():
            st.write(f"**第 {row['題號']} 題：{row['題目']}**")
            options = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
            user_answers[idx] = st.radio(
                f"選擇答案 (第 {row['題號']} 題)", 
                options, 
                index=None, 
                key=f"q_{idx}",
                label_visibility="collapsed"
            )
            st.divider()
            
        submit = st.form_submit_button("交卷並計算分數")
        
        if submit:
            score = 0
            correct_count = 0
            total_questions = len(exam_df)
            
            for idx, row in exam_df.iterrows():
                # 將選項內容轉回數字答案 (1, 2, 3, 4)
                options = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                correct_ans_str = options[int(row['正確答案'])-1]
                
                if user_answers[idx] == correct_ans_str:
                    correct_count += 1
                    st.success(f"第 {row['題號']} 題：正確！")
                else:
                    st.error(f"第 {row['題號']} 題：錯誤。正確答案是 ({row['正確答案']}) {correct_ans_str}")
            
            final_score = (correct_count / total_questions) * 100
            st.balloons()
            st.metric("測驗結果", f"{final_score:.1f} 分", f"答對 {correct_count} / {total_questions}")
            
            if final_score >= 70:
                st.success("恭喜及格！繼續保持！")
            else:
                st.warning("尚未及格，再多練習幾次吧！")
