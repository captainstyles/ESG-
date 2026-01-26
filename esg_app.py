import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="ESG 題庫練習", layout="centered")

# --- 讀取資料 ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("exam_data.csv", sep="|", encoding="utf-8-sig", engine="python")
        df.columns = df.columns.str.strip() 
        return df
    except Exception as e:
        st.error(f"❌ 讀取 CSV 失敗：{e}")
        return None

df = load_data()

if df is not None:
    # --- 初始化 Session State ---
    if 'order' not in st.session_state:
        st.session_state.order = list(range(len(df))) 
    if 'idx_in_order' not in st.session_state:
        st.session_state.idx_in_order = 0
    if 'show_ans' not in st.session_state:
        st.session_state.show_ans = False
    if 'wrong_questions' not in st.session_state:
        st.session_state.wrong_questions = set()  # 使用 set 避免重複收集同一題

    # --- 側邊欄 ---
    st.sidebar.header("⚙️ 練習設定")
    mode = st.sidebar.radio("出題模式", ["依序練習", "隨機挑戰", "❌ 錯題收集箱"])
    
    # 錯題箱數量提醒
    wrong_count = len(st.session_state.wrong_questions)
    if mode == "❌ 錯題收集箱":
        st.sidebar.info(f"目前收集箱內有 {wrong_count} 題")

    num_to_sample = st.sidebar.number_input(
        "設定隨機抽選題數", 
        min_value=1, 
        max_value=len(df) if mode != "❌ 錯題收集箱" else max(1, wrong_count), 
        value=min(80, len(df)) if mode == "隨機挑戰" else (wrong_count if mode == "❌ 錯題收集箱" else len(df)),
        disabled=(mode == "依序練習")
    )

    if st.sidebar.button("套用並重新開始"):
        if mode == "隨機挑戰":
            st.session_state.order = random.sample(range(len(df)), int(num_to_sample))
        elif mode == "❌ 錯題收集箱":
            if wrong_count > 0:
                # 從錯題紀錄中抽出題目
                st.session_state.order = random.sample(list(st.session_state.wrong_questions), min(int(num_to_sample), wrong_count))
            else:
                st.sidebar.warning("目前沒有錯題紀錄喔！")
                st.session_state.order = list(range(len(df)))
        else:
            st.session_state.order = list(range(len(df)))
            
        st.session_state.idx_in_order = 0
        st.session_state.show_ans = False
        st.rerun()

    if st.sidebar.button("清空錯題紀錄"):
        st.session_state.wrong_questions = set()
        st.sidebar.success("紀錄已清空！")
        st.rerun()

    # --- 主畫面 ---
    st.title("🌱 ESG 模擬練習")
    
    current_total = len(st.session_state.order)
    current_actual_idx = st.session_state.order[st.session_state.idx_in_order]
    row = df.iloc[current_actual_idx]
    
    st.caption(f"模式: {mode} | 本次總數: {current_total} | 進度: {st.session_state.idx_in_order + 1} / {current_total}")
    st.progress((st.session_state.idx_in_order + 1) / current_total)

    with st.container(border=True):
        st.info(f"**原始題庫編號：第 {row['題號']} 題**")
        st.subheader(row['題目'])
        
        opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
        ans = st.radio("請選擇答案：", opts, index=None, key=f"q_{current_actual_idx}_{st.session_state.idx_in_order}")

    # --- 按鈕區 ---
    col_prev, col_submit, col_next = st.columns([1, 1, 1])
    
    with col_prev:
        if st.button("⬅️ 上一題", use_container_width=True):
            if st.session_state.idx_in_order > 0:
                st.session_state.idx_in_order -= 1
                st.session_state.show_ans = False
                st.rerun()

    with col_submit:
        if st.button("✅ 提交答案", use_container_width=True):
            if ans: 
                st.session_state.show_ans = True
                # 檢查是否正確，若錯誤則加入錯題集
                correct_num = int(row['正確答案'])
                if ans != opts[correct_num - 1]:
                    st.session_state.wrong_questions.add(current_actual_idx)
            else:
                st.warning("請先選擇一個選項！")

    if st.session_state.show_ans:
        correct_num = int(row['正確答案'])
        correct_text = opts[correct_num - 1]
        if ans == correct_text:
            st.success(f"🎯 正確！答案是 ({correct_num})")
        else:
            st.error(f"❌ 錯誤！正確答案是 ({correct_num}) \n\n {correct_text}")
            st.info("💡 此題已自動加入「錯題收集箱」")
        
        with col_next:
            if st.button("下一題 ➡️", use_container_width=True):
                if st.session_state.idx_in_order < current_total - 1:
                    st.session_state.idx_in_order += 1
                    st.session_state.show_ans = False
                    st.rerun()
                else:
                    st.balloons()
                    st.success("測驗結束！")


