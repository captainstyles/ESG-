import streamlit as st
import pandas as pd
import random

# 設定網頁標題
st.set_page_config(page_title="ESG 永續發展題庫練習", layout="wide")

# 初始化 Session State (錯題紀錄)
if 'wrong_questions' not in st.session_state:
    st.session_state.wrong_questions = pd.DataFrame(columns=['題號', '題目', '正確答案'])

def load_data():
    try:
        df = pd.read_csv('exam_data.csv', sep='|', encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"讀取失敗: {e}")
        return None

df = load_data()

if df is not None:
    st.title("🌱 ESG 永續發展基礎能力測驗")
    
    # 側邊欄設定
    st.sidebar.header("功能選單")
    mode = st.sidebar.radio("選擇模式", ["分段練習", "隨機挑戰", "錯題收集箱"])
    
    total_q = len(df)
    exam_df = pd.DataFrame() # 初始化

    if mode == "分段練習":
        chunk_size = 100
        ranges = [f"{i+1} - {min(i+chunk_size, total_q)}" for i in range(0, total_q, chunk_size)]
        selected_range = st.sidebar.selectbox("選擇題目範圍", ranges)
        start_idx = int(selected_range.split(" - ")[0]) - 1
        end_idx = int(selected_range.split(" - ")[1])
        exam_df = df.iloc[start_idx:end_idx].copy()
        
    elif mode == "隨機挑戰":
        num_q = st.sidebar.slider("抽取題數", 10, 100, 80)
        if st.sidebar.button("重新抽題"):
            st.rerun()
        exam_df = df.sample(n=min(num_q, total_q)).copy()
        
    elif mode == "錯題收集箱":
        if len(st.session_state.wrong_questions) == 0:
            st.info("目前沒有錯題紀錄，繼續加油！")
        else:
            st.subheader("📝 我的錯題紀錄表")
            st.dataframe(st.session_state.wrong_questions, use_container_width=True)
            if st.button("清空所有紀錄"):
                st.session_state.wrong_questions = pd.DataFrame(columns=['題號', '題目', '正確答案'])
                st.rerun()

    # 練習介面
    if not exam_df.empty:
        # 使用 st.form 會導致頁面一次性刷新，適合交卷邏輯
        with st.form("exam_form"):
            user_answers = {}
            for idx, row in exam_df.iterrows():
                st.write(f"### 第 {row['題號']} 題")
                st.write(row['題目'])
                options = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                user_answers[idx] = st.radio(
                    f"選擇答案", options, index=None, key=f"q_{idx}", label_visibility="collapsed"
                )
                st.divider()
            
            submit = st.form_submit_button("交卷並查看結果")
            
            if submit:
                score_count = 0
                temp_wrong = []
                
                # 交卷後的處理邏輯
                for idx, row in exam_df.iterrows():
                    options = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                    correct_ans_idx = int(row['正確答案']) - 1
                    correct_text = options[correct_ans_idx]
                    
                    # 重新顯示題目內容與結果回饋 (這會顯示在 form 的下方)
                    if user_answers[idx] == correct_text:
                        score_count += 1
                        st.success(f"第 {row['題號']} 題：正確！ ✅")
                    else:
                        st.error(f"第 {row['題號']} 題：錯誤！ ❌")
                        st.info(f"💡 正確答案是：({row['正確答案']}) {correct_text}")
                        temp_wrong.append({'題號': row['題號'], '題目': row['題目'], '正確答案': correct_text})
                
                # 更新錯題紀錄
                if temp_wrong:
                    new_wrongs = pd.DataFrame(temp_wrong)
                    st.session_state.wrong_questions = pd.concat([st.session_state.wrong_questions, new_wrongs]).drop_duplicates(subset=['題號'])
                
                final_score = (score_count / len(exam_df)) * 100
                st.metric("總分", f"{final_score:.1f} 分", f"答對 {score_count} 題")
                if final_score >= 70: st.balloons()
