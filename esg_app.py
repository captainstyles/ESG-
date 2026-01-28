import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="ESG 證照測驗", layout="centered")

# --- 讀取資料 ---
@st.cache_data
def load_data():
    try:
        # 讀取 CSV，設定分隔符號為 |
        df = pd.read_csv("exam_data.csv", sep="|", encoding="utf-8-sig", engine="python")
        df.columns = df.columns.str.strip() 
        return df
    except Exception as e:
        st.error(f"❌ 讀取 CSV 失敗，請檢查檔案格式或檔名：{e}")
        return None

df = load_data()

if df is not None:
    # --- 1. 初始化 Session State ---
    if 'order' not in st.session_state:
        st.session_state.order = list(range(len(df))) 
    if 'idx_in_order' not in st.session_state:
        st.session_state.idx_in_order = 0
    if 'show_ans' not in st.session_state:
        st.session_state.show_ans = False
    if 'wrong_questions' not in st.session_state:
        st.session_state.wrong_questions = set()
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {} # 格式 {題目索引: 使用者選擇的文字}
    if 'finished' not in st.session_state:
        st.session_state.finished = False # 是否進入結算頁面

    # --- 側邊欄：功能設定 ---
    st.sidebar.header("⚙️ 練習設定")
    
    # 功能：分段選擇 (每100題一段)
    chunk_size = 100
    total_q_count = len(df)
    chunks = [f"{i+1} - {min(i+chunk_size, total_q_count)}" for i in range(0, total_q_count, chunk_size)]
    
    mode = st.sidebar.radio("出題模式", ["分段練習", "隨機挑戰 (80題)", "❌ 錯題收集箱"])
    
    selected_chunk = None
    if mode == "分段練習":
        selected_chunk = st.sidebar.selectbox("選擇題庫區段", chunks)

    if st.sidebar.button("套用並重新開始"):
        # 重置所有狀態
        st.session_state.user_answers = {}
        st.session_state.idx_in_order = 0
        st.session_state.show_ans = False
        st.session_state.finished = False
        
        if mode == "分段練習":
            start_idx = int(selected_chunk.split(" - ")[0]) - 1
            end_idx = int(selected_chunk.split(" - ")[1])
            st.session_state.order = list(range(start_idx, end_idx))
        elif mode == "隨機挑戰 (80題)":
            st.session_state.order = random.sample(range(len(df)), min(80, len(df)))
        elif mode == "❌ 錯題收集箱":
            if len(st.session_state.wrong_questions) > 0:
                st.session_state.order = list(st.session_state.wrong_questions)
            else:
                st.sidebar.warning("目前沒有錯題紀錄！")
                st.stop()
        st.rerun()

    if st.sidebar.button("清空錯題紀錄"):
        st.session_state.wrong_questions = set()
        st.sidebar.success("已清空")

    # --- 主畫面邏輯 ---
    st.title("🌱 ESG 模擬練習系統")

    # 如果已經結束，顯示統計頁面
    if st.session_state.finished:
        st.header("📊 本次練習結算")
        
        # 計算答對題數
        score_count = 0
        for idx in st.session_state.order:
            row_data = df.iloc[idx]
            # 取得正確答案文字
            correct_ans_num = int(row_data['正確答案'])
            correct_ans_text = str(row_data[f'選項{correct_ans_num}'])
            # 比對使用者答案
            if st.session_state.user_answers.get(idx) == correct_ans_text:
                score_count += 1
        
        total_in_session = len(st.session_state.order)
        final_score = (score_count / total_in_session) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("答對題數", f"{score_count} / {total_in_session}")
        col2.metric("換算得分", f"{final_score:.1f} 分")
        col3.metric("及格門檻", "70.0 分")
        
        if final_score >= 70:
            st.balloons()
            st.success(f"🎊 恭喜及格！達到正式考試標準。")
        else:
            st.error(f"💀 尚未及格... 距離及格還差 {max(0, int(total_in_session*0.7) - score_count)} 題，加油！")
        
        if st.button("重新開始"):
            st.session_state.finished = False
            st.session_state.idx_in_order = 0
            st.session_state.user_answers = {}
            st.rerun()
            
    else:
        # 進行中的練習畫面
        current_total = len(st.session_state.order)
        current_actual_idx = st.session_state.order[st.session_state.idx_in_order]
        row = df.iloc[current_actual_idx]

        st.caption(f"模式：{mode} | 進度：{st.session_state.idx_in_order + 1} / {current_total}")
        st.progress((st.session_state.idx_in_order + 1) / current_total)

        # 顯示題目
        with st.container(border=True):
            st.info(f"**題號：{row['題號']}**")
            st.subheader(row['題目'])
            
            opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
            
            # 從紀錄中找回之前的選項
            prev_choice = st.session_state.user_answers.get(current_actual_idx, None)
            try:
                def_idx = opts.index(prev_choice) if prev_choice in opts else None
            except:
                def_idx = None

            ans = st.radio("您的選擇：", opts, index=def_idx, key=f"q_{current_actual_idx}")
            
            # 即時儲存選擇
            if ans:
                st.session_state.user_answers[current_actual_idx] = ans

        # 按鈕區
        col_prev, col_submit, col_next = st.columns([1, 1, 1])
        
        with col_prev:
            if st.button("⬅️ 上一題", disabled=(st.session_state.idx_in_order == 0), use_container_width=True):
                st.session_state.idx_in_order -= 1
                st.session_state.show_ans = False
                st.rerun()

        with col_submit:
            if st.button("🔍 看答案", use_container_width=True):
                st.session_state.show_ans = True

        with col_next:
            is_last = (st.session_state.idx_in_order == current_total - 1)
            btn_label = "📊 結算成績" if is_last else "下一題 ➡️"
            if st.button(btn_label, type="primary" if is_last else "secondary", use_container_width=True):
                if is_last:
                    st.session_state.finished = True
                else:
                    st.session_state.idx_in_order += 1
                    st.session_state.show_ans = False
                st.rerun()

        # 顯示即時回饋
        if st.session_state.show_ans:
            correct_num = int(row['正確答案'])
            correct_text = opts[correct_num - 1]
            if ans == correct_text:
                st.success(f"🎯 正確！")
            else:
                st.error(f"❌ 錯誤！正確答案是：({correct_num}) {correct_text}")
                st.session_state.wrong_questions.add(current_actual_idx)
