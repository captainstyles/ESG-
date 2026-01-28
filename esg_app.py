import streamlit as st
import pandas as pd

# 1. 頁面基本配置
st.set_page_config(page_title="ESG 永續發展題庫系統", layout="wide")

# 2. 初始化所有狀態 (Session State)
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'exam_df' not in st.session_state: st.session_state.exam_df = pd.DataFrame()
if 'wrong_questions' not in st.session_state:
    st.session_state.wrong_questions = pd.DataFrame(columns=['題號', '題目', '選項1', '選項2', '選項3', '選項4', '正確答案'])

# 3. 讀取資料函式
@st.cache_data
def load_data():
    try:
        # 使用你 CSV 的分隔符號 |
        return pd.read_csv('exam_data.csv', sep='|', encoding='utf-8')
    except:
        return None

df = load_data()

if df is not None:
    st.title("🌱 ESG 永續發展題庫練習系統 (840題全功能版)")
    
    # --- 側邊欄：功能控制區 ---
    st.sidebar.header("⚙️ 測驗設定")
    mode = st.sidebar.radio("測驗模式", ["分段練習", "隨機挑戰", "錯題重溫"])
    
    # 自定義數量功能
    num_to_test = st.sidebar.slider("每次練習題目數量", 5, 100, 20)
    
    if mode == "分段練習":
        chunk_size = 100
        total_q = len(df)
        ranges = [f"{i+1}-{min(i+chunk_size, total_q)}" for i in range(0, total_q, chunk_size)]
        selected_range = st.sidebar.selectbox("選擇題號範圍起始", ranges)
        start_idx = int(selected_range.split('-')[0]) - 1

    # 生成考卷按鈕
    if st.sidebar.button("✨ 產生考卷 / 重新抽題", use_container_width=True):
        st.session_state.submitted = False
        if mode == "分段練習":
            # 從選定的範圍起始點，抓取使用者自訂數量的題目
            st.session_state.exam_df = df.iloc[start_idx : start_idx + num_to_test].copy()
        elif mode == "隨機挑戰":
            # 使用 pandas 內建 sample 功能實現隨機
            st.session_state.exam_df = df.sample(n=min(num_to_test, len(df))).copy()
        elif mode == "錯題重溫":
            if not st.session_state.wrong_questions.empty:
                st.session_state.exam_df = st.session_state.wrong_questions.sample(n=min(num_to_test, len(st.session_state.wrong_questions))).copy()
            else:
                st.session_state.exam_df = pd.DataFrame()
        st.rerun()

    # --- 畫面顯示區 ---
    if mode == "錯題重溫" and st.session_state.wrong_questions.empty:
        st.info("目前沒有錯題紀錄。當你在其他模式答錯時，系統會自動收集到這裡！")
    
    elif not st.session_state.exam_df.empty:
        exam_df = st.session_state.exam_df
        user_answers = {}

        # 頂部評分看板
        if st.session_state.submitted:
            correct_total = 0
            for idx, row in exam_df.iterrows():
                opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                if st.session_state.get(f"q_{idx}") == opts[int(row['正確答案'])-1]:
                    correct_total += 1
            
            score = (correct_total / len(exam_df)) * 100
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("得分", f"{score:.1f}")
            c2.metric("答對題數", f"{correct_total} / {len(exam_df)}")
            c3.success("及格！" if score >= 70 else "再加油！")
            st.divider()

        # 題目區
        for idx, row in exam_df.iterrows():
            st.write(f"**Q{row['題號']}**: {row['題目']}")
            opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
            
            user_answers[idx] = st.radio(
                f"options_{idx}", opts, index=None, key=f"q_{idx}",
                label_visibility="collapsed", disabled=st.session_state.submitted
            )

            if st.session_state.submitted:
                correct_idx = int(row['正確答案']) - 1
                correct_text = opts[correct_idx]
                if user_answers[idx] == correct_text:
                    st.success(f"✅ 正確")
                else:
                    st.error(f"❌ 錯誤（你的選擇：{user_answers[idx] if user_answers[idx] else '未作答'}）")
                    st.info(f"💡 正確答案：({row['正確答案']}) {correct_text}")
            st.write("")

        # 底部按鈕
        col_left, col_right = st.columns(2)
        with col_left:
            if not st.session_state.submitted:
                if st.button("🏁 完成交卷", type="primary", use_container_width=True):
                    st.session_state.submitted = True
                    # 紀錄錯題邏輯
                    new_wrongs = []
                    for idx, row in exam_df.iterrows():
                        opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                        if user_answers[idx] != opts[int(row['正確答案'])-1]:
                            new_wrongs.append(row)
                    if new_wrongs:
                        st.session_state.wrong_questions = pd.concat([st.session_state.wrong_questions, pd.DataFrame(new_wrongs)]).drop_duplicates(subset=['題號'])
                    st.rerun()
        with col_right:
            if st.button("🔄 重新練習 / 清空", use_container_width=True):
                st.session_state.submitted = False
                st.rerun()
else:
    st.warning("請確認目錄下有 exam_data.csv 檔案。")
