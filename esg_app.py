import streamlit as st
import pandas as pd

# 1. 頁面基本配置
st.set_page_config(page_title="ESG 永續發展題庫系統", layout="wide")

# 2. 初始化所有狀態 (Session State)
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'exam_df' not in st.session_state: st.session_state.exam_df = pd.DataFrame()
if 'wrong_questions' not in st.session_state:
    st.session_state.wrong_questions = pd.DataFrame(columns=['題號', '題目', '正確答案'])

# 3. 讀取資料函式
@st.cache_data # 增加快取，讀取速度會變快
def load_data():
    try:
        return pd.read_csv('exam_data.csv', sep='|', encoding='utf-8')
    except:
        return None

df = load_data()

# 4. 主程式邏輯
if df is not None:
    st.title("🌱 ESG 永續發展基礎能力測驗系統")
    st.caption(f"目前題庫總數：{len(df)} 題")

    # --- 側邊欄：功能控制區 ---
    st.sidebar.header("⚙️ 測驗設定")
    mode = st.sidebar.radio("測驗模式", ["分段練習", "隨機挑戰 (80題)", "錯題重溫"])
    
    if mode == "分段練習":
        chunk_size = 100
        total_q = len(df)
        ranges = [f"{i+1}-{min(i+chunk_size, total_q)}" for i in range(0, total_q, chunk_size)]
        selected_range = st.sidebar.selectbox("選擇題號範圍", ranges)
    
    if st.sidebar.button("✨ 產生考卷 / 重新測驗", use_container_width=True):
        st.session_state.submitted = False
        if mode == "分段練習":
            start, end = map(int, selected_range.split('-'))
            st.session_state.exam_df = df.iloc[start-1:end].copy()
        elif mode == "隨機挑戰 (80題)":
            st.session_state.exam_df = df.sample(n=80).copy()
        elif mode == "錯題重溫":
            st.session_state.exam_df = st.session_state.wrong_questions.copy()
        st.rerun()

    # --- 畫面顯示區 ---
    if mode == "錯題重溫" and st.session_state.wrong_questions.empty:
        st.info("目前沒有錯題紀錄，快去練習吧！")
    
    elif not st.session_state.exam_df.empty:
        exam_df = st.session_state.exam_df
        user_answers = {}

        # 頂部評分板 (交卷後顯示)
        if st.session_state.submitted:
            correct_total = 0
            # 預先計算分數
            for idx, row in exam_df.iterrows():
                opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                if st.session_state.get(f"q_{idx}") == opts[int(row['正確答案'])-1]:
                    correct_total += 1
            
            score = (correct_total / len(exam_df)) * 100
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("得分", f"{score:.1f}")
            col_b.metric("答對題數", f"{correct_total} / {len(exam_df)}")
            col_c.write("🎉" if score >= 70 else "💪 再接再厲")
            st.divider()

        # 題目渲染區
        for idx, row in exam_df.iterrows():
            with st.container():
                st.write(f"**Q{row['題號']}**: {row['題目']}")
                opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                
                # 選項
                user_answers[idx] = st.radio(
                    f"Options_{idx}", opts, index=None, key=f"q_{idx}",
                    label_visibility="collapsed", disabled=st.session_state.submitted
                )

                # 交卷後的逐題解析
                if st.session_state.submitted:
                    correct_idx = int(row['正確答案']) - 1
                    correct_text = opts[correct_idx]
                    
                    if user_answers[idx] == correct_text:
                        st.success("✅ 回答正確")
                    else:
                        st.error(f"❌ 回答錯誤（你的選擇：{user_answers[idx] if user_answers[idx] else '未作答'}）")
                        st.info(f"💡 正確答案是：({row['正確答案']}) {correct_text}")
                st.write("") # 間距

        # 底部按鈕
        if not st.session_state.submitted:
            if st.button("🏁 完成所有題目，交卷！", type="primary", use_container_width=True):
                st.session_state.submitted = True
                
                # 自動更新錯題箱
                temp_wrongs = []
                for idx, row in exam_df.iterrows():
                    opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
                    correct_text = opts[int(row['正確答案'])-1]
                    if user_answers[idx] != correct_text:
                        temp_wrongs.append({'題號': row['題號'], '題目': row['題目'], '正確答案': correct_text})
                
                if temp_wrongs:
                    new_wrongs = pd.DataFrame(temp_wrongs)
                    st.session_state.wrong_questions = pd.concat([st.session_state.wrong_questions, new_wrongs]).drop_duplicates(subset=['題號'])
                
                st.rerun()
        else:
            if st.button("🔄 重新測驗", use_container_width=True):
                st.session_state.submitted = False
                st.rerun()
else:
    st.warning("找不到 exam_data.csv，請確認檔案已上傳至 GitHub 並正確設定分隔符號 |")
