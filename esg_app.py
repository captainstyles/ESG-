import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="ESG 題庫練習", layout="centered")

# --- 讀取資料 ---
@st.cache_data
def load_data():
    try:
        # 使用 utf-8-sig 讀取，處理 CSV 內容
        df = pd.read_csv("exam_data.csv", sep="|", encoding="utf-8-sig", engine="python")
        df.columns = df.columns.str.strip() 
        return df
    except Exception as e:
        st.error(f"❌ 讀取 CSV 失敗：{e}")
        return None

df = load_data()

if df is not None:
    # --- 初始化 Session State ---
    # order 儲存的是目前測驗組的索引清單
    if 'order' not in st.session_state:
        st.session_state.order = list(range(len(df))) 
    if 'idx_in_order' not in st.session_state:
        st.session_state.idx_in_order = 0
    if 'show_ans' not in st.session_state:
        st.session_state.show_ans = False

    # --- 側邊欄 ---
    st.sidebar.header("⚙️ 練習設定")
    mode = st.sidebar.radio("出題模式", ["依序練習", "隨機挑戰"])
    
    # 新增：自選隨機題數功能
    num_to_sample = st.sidebar.number_input(
        "設定隨機抽選題數", 
        min_value=1, 
        max_value=len(df), 
        value=min(80, len(df)) if mode == "隨機挑戰" else len(df),
        disabled=(mode == "依序練習") # 依序練習時不需設定題數
    )

    if st.sidebar.button("套用並重新開始"):
        if mode == "隨機挑戰":
            # 從總題庫中隨機抽出指定數量的索引
            st.session_state.order = random.sample(range(len(df)), int(num_to_sample))
        else:
            # 依序練習則載入全部索引
            st.session_state.order = list(range(len(df)))
            
        st.session_state.idx_in_order = 0
        st.session_state.show_ans = False
        st.rerun()

    st.sidebar.divider()
    
    # 這裡的總數會根據隨機抽選後的結果變動
    current_total = len(st.session_state.order)
    
    jump_q = st.sidebar.number_input(f"跳轉至目前進度 (1-{current_total})", 1, current_total, st.session_state.idx_in_order + 1)
    if st.sidebar.button("立刻跳轉"):
        st.session_state.idx_in_order = int(jump_q) - 1
        st.session_state.show_ans = False
        st.rerun()

    # --- 主畫面 ---
    st.title("🌱 ESG 模擬練習 (760題庫版)")
    
    # 取得目前題目在原始 df 中的索引
    current_actual_idx = st.session_state.order[st.session_state.idx_in_order]
    row = df.iloc[current_actual_idx]
    
    st.caption(f"模式: {mode} | 本次測驗總題數: {current_total} | 目前進度: {st.session_state.idx_in_order + 1} / {current_total}")
    st.progress((st.session_state.idx_in_order + 1) / current_total)

    with st.container(border=True):
        st.info(f"**原始題庫編號：第 {row['題號']} 題**")
        st.subheader(row['題目'])
        
        opts = [str(row['選項1']), str(row['選項2']), str(row['選項3']), str(row['選項4'])]
        # 使用唯一 key 避免 radio 按鈕狀態衝突
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
            else:
                st.warning("請先選擇一個選項再提交！")

    if st.session_state.show_ans:
        correct_num = int(row['正確答案'])
        correct_text = opts[correct_num - 1]
        if ans == correct_text:
            st.success(f"🎯 正確！答案是 ({correct_num})")
        else:
            st.error(f"❌ 錯誤！正確答案是 ({correct_num}) \n\n {correct_text}")
        
        with col_next:
            if st.button("下一題 ➡️", use_container_width=True):
                if st.session_state.idx_in_order < current_total - 1:
                    st.session_state.idx_in_order += 1
                    st.session_state.show_ans = False
                    st.rerun()
                else:
                    st.balloons()

                    st.success("恭喜！您已完成本次設定的所有題目！")
