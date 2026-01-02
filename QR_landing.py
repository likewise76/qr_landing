import streamlit as st
import re

# 1. 페이지 설정 (브라우저 탭 이름, 아이콘)
st.set_page_config(page_title="대성쎌틱 명함 제작소", page_icon="🔥", layout="centered")

# 2. 스타일 커스터마이징 (심플하고 깔끔하게)
st.markdown("""
    <style>
    /* 전체 배경색 */
    .stApp {
        background-color: #ffffff;
    }
    /* 메인 헤더 스타일 */
    .main-header {
        font-size: 28px; 
        font-weight: 700; 
        color: #111; 
        text-align: center; 
        margin-bottom: 10px;
        padding-top: 20px;
    }
    /* 서브 설명 텍스트 */
    .sub-text {
        font-size: 16px;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    /* 입력 폼 스타일 개선 */
    div[data-testid="stForm"] {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #eee;
    }
    /* 생성 버튼 스타일 (검은색 강조) */
    div.stButton > button {
        width: 100%;
        background-color: #222;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 12px;
        border: none;
        transition: background-color 0.3s;
    }
    div.stButton > button:hover {
        background-color: #444;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 화면 구성
st.markdown('<div class="main-header">🔥 대리점 모바일 명함 제작소</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">정보를 입력하면 웹 게시용 HTML 파일이 생성됩니다.<br>생성된 파일을 다운로드하세요.</div>', unsafe_allow_html=True)

# 4. 입력 폼
with st.form("info_form"):
    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("상호명", placeholder="예: 대성쎌틱 서구점")
    with col2:
        filename_input = st.text_input("파일 이름 (영문 권장)", placeholder="예: seogu")
        st.caption("※ 나중에 인터넷 주소(URL)의 뒷부분이 됩니다.")

    phone_number = st.text_input("전화번호 (- 포함)", placeholder="예: 010-1234-5678")
    price_url = st.text_input("단가표 링크 (선택사항)", placeholder="http://...")

    # 여백
    st.markdown("###") 
    
    submitted = st.form_submit_button("✨ HTML 명함 파일 생성하기")

# 5. 로직 및 결과 처리
if submitted:
    if not store_name or not phone_number:
        st.error("⚠️ 상호명과 전화번호는 필수 입력 사항입니다.")
    else:
        # 파일명 자동 정제 (영문, 숫자만 남김)
        save_name = filename_input if filename_input else "index"
        save_name = re.sub(r'[^a-zA-Z0-9_-]', '', save_name)
        full_filename = f"{save_name}.html"

        # --- [최종 확정된 HTML 템플릿: 모바일 최적화, 흑백 심플] ---
        html_code = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{store_name}</title>
    <style>
        body {{
            font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
            margin: 0; padding: 0; background-color: #f9f9f9;
            color: #333; display: flex; flex-direction: column;
            align-items: center; min-height: 100vh;
        }}
        .container {{
            width: 100%; max-width: 600px; background-color: #fff;
            padding: 50px 20px; box-sizing: border-box;
            text-align: center; border-bottom: 1px solid #eee;
        }}
        h1 {{ font-size: 26px; margin-bottom: 15px; font-weight: bold; word-break: keep-all; }}
        p {{ font-size: 17px; color: #555; margin-bottom: 40px; line-height: 1.6; }}
        
        .btn {{
            display: block; width: 100%; max-width: 320px; margin: 12px auto;
            padding: 16px 0; font-size: 17px; font-weight: bold;
            text-decoration: none; border-radius: 8px;
            background-color: #fff; color: #000; border: 2px solid #000;
            transition: background-color 0.2s;
        }}
        .btn:hover {{ background-color: #f0f0f0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{store_name}</h1>
        <p>친절하고 정확한 상담 도와드리겠습니다.<br>아래 버튼을 눌러주세요.</p>
        
        <a href="tel:{phone_number}" class="btn">전화 상담 연결</a>
        
        {'<a href="' + price_url + '" class="btn" target="_blank">단가표 보기</a>' if price_url else ''}
    </div>
</body>
</html>"""

        # 결과 화면
        st.success(f"✅ 생성 완료! 아래 버튼을 눌러 저장하세요.")
        
        # 다운로드 버튼
        st.download_button(
            label=f"📥 '{full_filename}' 파일 다운로드",
            data=html_code,
            file_name=full_filename,
            mime="text/html"
        )
        
        # 안내 메시지
        st.info(f"""
        **💡 사용 방법**
        1. 위 파일을 다운로드합니다.
        2. 담당자에게 전달하여 **GitHub 저장소**에 업로드 요청하세요.
        """)