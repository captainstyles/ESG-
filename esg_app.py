import streamlit as st
import pandas as pd

# 1. 頁面基本配置
st.set_page_config(page_title="ESG 永續發展題庫系統", layout="wide")

# 2. 初始化 Session State
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'exam_df' not in st.session_state: st.session_state.exam_df = pd.DataFrame()
if 'wrong_questions' not in st.session_state:
    st.session_state.wrong_questions = pd.DataFrame(columns=['題號', '題目', '選項1', '選項2', '選項3', '選項4', '正確答案'])

# 3. 讀取資料
@st.cache_data
def load_data():
    try:
        # 使用分隔符號 |
        return pd.read_csv('exam_data.csv', sep='|', encoding='utf-8')
    except:
        return None

df = load_data()

if df is not None:
    st.title("🌱 ESG 永續發展題庫練習系統")
    
    # --- 側邊欄：功能控制區 ---
    st.sidebar.header("⚙️ 測驗設定")
    # 新增「全題庫挑戰」選項
    mode = st.sidebar.radio("測驗模式", ["分段練習", "隨機挑戰", "全題庫挑戰 (840題)", "錯題重溫"])
    
    # 數量設定（僅針對分段與隨機模式）
    if mode in ["分段練習", "隨機挑戰"]:
        num_to_test = st.sidebar.slider("練習題目數量", 5, 100, 20)
    
    if mode == "分段練習":
        chunk_size = 100
        total_q = len(df)
        ranges = [f"{i+1}-{min(i+chunk_size, total_q)}" for i in range(0, total_q, chunk_size)]
        selected_range = st.sidebar.selectbox("選擇題號起始範圍", ranges)
        start_idx = int(selected_range.split('-')[0]) - 1

    # 生成考卷按鈕
    if st.sidebar.button("✨ 產生考卷 / 開始練習", use_container_width=True):
        st.session_state.submitted = False
        if mode == "分段練習":
            st.session_state.exam_df = df.iloc[start_idx : start_idx + num_to_test].copy()
        elif mode == "隨機挑戰":
            st.session_state.exam_df = df.sample(n=min(num_to_test, len(df))).copy()
        elif mode == "全題庫挑戰 (840題)":
            st.session_state.exam_df = df.copy() # 載入全部資料
        elif mode == "錯題重溫":
            st.session_state.exam_df = st.session_state.wrong_questions.copy()
        st.rerun()

    # --- 畫面顯示區 ---
    if mode == "全題庫挑戰 (840題)":
        st.warning("⚠️ 警告：目前為 840 題全量模式，交卷時運算量較大，請耐心等候。")

    if not st.session_state.exam_df.empty:
        exam_df = st.session_state.exam_df
        user_answers = {}

        # 交卷後的評分看板
        if st.session_state.submitted:
            correct_total = 0
            for idx, row in exam_df.iterrows():
                opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                if st.session_state.get(f"q_{idx}") == opts[int(row['正確答案'])-1]:
                    correct_total += 1
            score = (correct_total / len(exam_df)) * 100
            st.success(f"測驗完成！總分：{score:.1f} | 答對題數：{correct_total} / {len(exam_df)}")
            st.divider()

        # 逐題渲染
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
                    st.error(f"❌ 錯誤！正確答案是：({row['正確答案']}) {correct_text}")
            st.divider()

        # 底部按鈕區
        if not st.session_state.submitted:
            if st.button("🏁 完成交卷", type="primary", use_container_width=True):
                st.session_state.submitted = True
                # 紀錄錯題
                new_wrongs = []
                for idx, row in exam_df.iterrows():
                    opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                    if user_answers[idx] != opts[int(row['正確答案'])-1]:
                        new_wrongs.append(row)
                if new_wrongs:
                    st.session_state.wrong_questions = pd.concat([st.session_state.wrong_questions, pd.DataFrame(new_wrongs)]).drop_duplicates(subset=['題號'])
                st.rerun()
        else:
            if st.button("🔄 重新測驗", use_container_width=True):
                st.session_state.submitted = False
                st.rerun()
else:
    st.info("請先從左側選擇模式並點擊『產生考卷』")
