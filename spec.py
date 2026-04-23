def main():
    render_header()
    st.markdown('<div class="main-title">📋 품질 통합 관리 시스템</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📄 고객 사양서", "⚖️ 품질 보증 기준"])

    with tab1:
        df_cust = load_data(EXCEL_FILE)

        if df_cust is not None:
            # 데이터 전처리
            df_cust = df_cust.dropna(subset=[df_cust.columns[0]])
            for col in df_cust.columns:
                df_cust[col] = df_cust[col].astype(str).str.strip()

            customer_list = df_cust.iloc[:, 0].tolist()

            # --- [변경 구간: 메인 화면 상단에 검색창 배치] ---
            st.markdown("### 🔍 고객사 검색 및 선택")
            
            # 관리자 전용 추가 버튼을 검색창 옆에 배치
            col_search, col_add = st.columns([8, 2])
            
            with col_search:
                sel_idx = st.selectbox(
                    "조회할 업체를 선택하거나 입력하세요.",
                    options=list(range(len(df_cust))),
                    format_func=lambda i: customer_list[i],
                    index=None,
                    placeholder="업체명을 입력하세요 (예: 한진철관)",
                    key="main_customer_select"
                )

            with col_add:
                if st.session_state.is_admin:
                    if st.button("➕ 고객사 추가", use_container_width=True):
                        st.session_state.show_add_form = True
                        st.session_state.edit_idx = None
                        st.rerun()
            
            st.markdown("---") # 구분선
            # ----------------------------------------------

            # 관리자 폼 렌더링
            if st.session_state.is_admin and st.session_state.show_add_form:
                render_add_form(df_cust)

            elif st.session_state.is_admin and st.session_state.edit_idx is not None:
                render_edit_form(df_cust, st.session_state.edit_idx)

            # 상세 정보 표시 영역
            elif sel_idx is not None:
                row = df_cust.iloc[sel_idx]
                
                # 상단 타이틀 및 관리 버튼
                title_col, btn_col = st.columns([7, 3])
                with title_col:
                    st.markdown(f'<div class="customer-title" style="margin-top:0;">■ {row.iloc[0]}</div>', unsafe_allow_html=True)
                
                with btn_col:
                    if st.session_state.is_admin:
                        a1, a2 = st.columns(2)
                        if a1.button("📝 수정", key="edit_btn", use_container_width=True):
                            st.session_state.edit_idx = sel_idx
                            st.session_state.show_add_form = False
                            st.rerun()
                        if a2.button("🗑️ 삭제", key="delete_btn", use_container_width=True):
                            st.session_state[f"confirm_delete_{sel_idx}"] = True

                # 삭제 확인 로직
                if st.session_state.get(f"confirm_delete_{sel_idx}", False):
                    st.warning(f"⚠️ **'{row.iloc[0]}'** 데이터를 영구 삭제하시겠습니까?")
                    d1, d2 = st.columns([1, 5])
                    if d1.button("확인 삭제", key="confirm_del"):
                        updated_df = df_cust.drop(index=sel_idx).reset_index(drop=True)
                        save_customer_data(updated_df)
                        st.session_state[f"confirm_delete_{sel_idx}"] = False
                        st.success("삭제되었습니다.")
                        st.rerun()
                    if d2.button("취소", key="cancel_del"):
                        st.session_state[f"confirm_delete_{sel_idx}"] = False
                        st.rerun()

                # 사양 정보 렌더링 (기존 동일)
                for i in range(1, len(row.index)):
                    col_n = row.index[i]
                    raw = row.iloc[i]
                    val = str(raw).strip() if pd.notna(raw) and str(raw).strip() not in ("", "nan") else "-"
                    is_sp = any(k in str(col_n) for k in ["특이사항", "주의", "마킹", "포장"])
                    c = "#E63946" if is_sp else "#495057"
                    st.markdown(f"""
                    <div class="notranslate" style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                        <div style="background-color: #F8F9FA; width: 100px; min-width: 100px; padding: 12px 6px; font-weight: bold; color: {c}; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 13px; line-height: 1.2;">{col_n}</div>
                        <div style="flex: 1; padding: 12px; background-color: white; font-size: 14px; line-height: 1.5; color: #212529;">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                # 아무것도 선택되지 않았을 때의 안내
                st.info("위의 검색창에서 고객사를 선택하면 상세 사양 정보가 표시됩니다.")

        render_admin_login() # 관리자 로그인은 여전히 사이드바 하단에 유지 (보안상 격리)