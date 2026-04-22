import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
import sys
import tempfile # 임시 파일 생성을 위해 추가

def load_data():
    if getattr(sys, 'frozen', False):
        current_path = os.path.dirname(sys.executable)
    else:
        current_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_path)

    file_candidates = ['고객 사양서.xlsx - Sheet1.csv', '고객 사양서.xlsx', '고객 사양서.csv']
    target_file = next((f for f in file_candidates if os.path.exists(f)), None)
    
    if not target_file:
        messagebox.showerror("파일 없음", "데이터 파일을 찾을 수 없습니다.")
        return None
    
    try:
        if target_file.endswith('.csv'):
            try: df = pd.read_csv(target_file, encoding='cp949')
            except: df = pd.read_csv(target_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(target_file)
        return df.fillna("-")
    except Exception as e:
        messagebox.showerror("오류", f"파일 로드 실패: {e}")
        return None

# --- 인쇄 함수 추가 ---
def print_spec(customer_name, row_data):
    try:
        # 임시 텍스트 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='cp949') as f:
            f.write(f"<{customer_name} 제작 규격서>\n")
            f.write("="*40 + "\n")
            for col, val in row_data.items():
                if col == row_data.index[0]: continue
                f.write(f"■ {col}\n   ㄴ {val}\n\n")
            f.write("="*40 + "\n")
            f_path = f.name
        
        # 메모장으로 파일 열기 (사용자가 직접 인쇄 버튼 누르도록)
        os.startfile(f_path)
    except Exception as e:
        messagebox.showerror("인쇄 오류", f"인쇄 파일을 만드는 중 오류가 발생했습니다: {e}")

def display_spec(row_data):
    for widget in scroll_content.winfo_children():
        widget.destroy()
    
    customer_name = row_data.iloc[0]
    
    # 상단 헤더 프레임 (타이틀 + 인쇄 버튼)
    header_f = tk.Frame(scroll_content, bg="white")
    header_f.pack(fill="x", pady=(0, 20))

    tk.Label(header_f, text=f"■ {customer_name} 상세 사양", font=("맑은 고딕", 18, "bold"), 
             bg="white", fg="black").pack(side="left")
    
    # [인쇄하기] 버튼 추가
    print_btn = tk.Button(header_f, text="🖨️ 사양 인쇄", font=("맑은 고딕", 10, "bold"),
                          bg="#F8F9FA", fg="#1A73E8", relief="groove", padx=15,
                          command=lambda: print_spec(customer_name, row_data))
    print_btn.pack(side="right")

    # 세로형 표 프레임
    table_frame = tk.Frame(scroll_content, bg="#CCCCCC", bd=1)
    table_frame.pack(fill="x")

    cols = list(row_data.index[1:])
    for col_name in cols:
        val = str(row_data[col_name])
        row_f = tk.Frame(table_frame, bg="white")
        row_f.pack(fill="x", pady=1)
        
        is_special = any(keyword in col_name for keyword in ["특이사항", "주의", "마킹"])
        content_fg = "red" if is_special else "black"
        content_font = ("맑은 고딕", 11, "bold") if is_special else ("맑은 고딕", 11)

        tk.Label(row_f, text=col_name, font=("맑은 고딕", 10, "bold"), 
                 bg="#F2F2F2", fg="#333333", width=18, anchor="nw", padx=15, pady=10).pack(side="left", fill="y")
        
        msg = tk.Message(row_f, text=val, font=content_font, bg="white", fg=content_fg,
                         width=550, anchor="w", padx=20, pady=10)
        msg.pack(side="left", fill="both", expand=True)

# 마우스 휠 스크롤 함수
def _on_mousewheel(event, canvas_obj):
    canvas_obj.yview_scroll(int(-1*(event.delta/120)), "units")

# UI 설정
root = tk.Tk()
root.title("한진철관 품질기술팀 - 사양 관리 시스템")
root.geometry("1150x850")
root.configure(bg="#F0F0F0")

df = load_data()

if df is not None:
    # 좌측 버튼 리스트
    list_frame = tk.Frame(root, bg="#F0F0F0")
    list_frame.pack(side="left", fill="y", padx=5, pady=10)
    
    list_canvas = tk.Canvas(list_frame, bg="#F0F0F0", highlightthickness=0, width=260)
    list_scroll = tk.Scrollbar(list_frame, orient="vertical", command=list_canvas.yview)
    btn_container = tk.Frame(list_canvas, bg="#F0F0F0")

    btn_container.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
    list_canvas.create_window((0, 0), window=btn_container, anchor="nw", width=250)
    list_canvas.configure(yscrollcommand=list_scroll.set)
    list_canvas.bind_all("<MouseWheel>", lambda e: _on_mousewheel(e, list_canvas))
    
    list_canvas.pack(side="left", fill="both", expand=True)
    list_scroll.pack(side="right", fill="y")

    for _, row in df.iterrows():
        name = str(row.iloc[0])
        btn = tk.Button(btn_container, text=name, font=("맑은 고딕", 9),
                        bg="#E1E1E1", fg="black", relief="raised", bd=1,
                        anchor="w", padx=10, pady=5, height=1,
                        activebackground="#D0D0D0",
                        command=lambda r=row: display_spec(r))
        btn.pack(fill="x", pady=1)

    # 우측 상세 정보
    detail_frame = tk.Frame(root, bg="white", relief="flat", bd=1)
    detail_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    main_canvas = tk.Canvas(detail_frame, bg="white", highlightthickness=0)
    main_scroll = tk.Scrollbar(detail_frame, orient="vertical", command=main_canvas.yview)
    scroll_content = tk.Frame(main_canvas, bg="white", padx=40, pady=30)

    scroll_content.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
    main_canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=800)
    main_canvas.configure(yscrollcommand=main_scroll.set)
    
    main_canvas.pack(side="left", fill="both", expand=True)
    main_scroll.pack(side="right", fill="y")
    
    tk.Label(scroll_content, text="← 목록에서 사양을 조회할 고객사를 선택하세요.", 
             font=("맑은 고딕", 11), bg="white", fg="#888888").pack(pady=250)

root.mainloop()
