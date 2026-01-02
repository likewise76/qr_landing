import streamlit as st
import re
import qrcode
import html
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
from github import Github

# --- [설정] 지역장님 정보 ---
GITHUB_USERNAME = "likewise76"   
REPO_NAME = "qr_address"         
# ---------------------------

# [보안 함수] 입력값 안전하게 세탁(Sanitizing)
def sanitize_filename(name: str) -> str:
    # 영문, 숫자, 언더바(_), 하이픈(-)만 남기고 제거
    cleaned = re.sub(r'[^a-zA-Z0-9_-]', '', (name or '').strip())
    return cleaned

def sanitize_store_name(name: str) -> str:
    # HTML 태그를 무력화 (XSS 방지)
    return html.escape((name or '').strip())

def sanitize_phone(phone: str) -> str:
    # 숫자만 추출 (하이픈 제거)
    digits = re.sub(r'[^0-9]', '', (phone or ''))
    return digits

def normalize_http_url(u: str) -> str:
    u = (u or '').strip()
    if not u:
        return ''
    if u.startswith('www.'):
        u = 'https://' + u
    try:
        p = urlparse(u)
        if not p.scheme: # http/https가 없으면 붙여줌
            u = 'https://' + u
            p = urlparse(u)
        if p.scheme not in ('http', 'https'): # 이상한 프로토콜 차단
            return ''
    except:
        return ''
    return u

# 1. 페이지 설정
st.set_page_config(page_title="대성쎌틱 대리점 QR생성기", layout="centered")

# 2. 스타일 설정
st.markdown("""
    <style>
    .stApp {background-color: #ffffff;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
    
    .main-header {font-size: 28px; font-weight: 700; color: #111; text-align: center; margin-bottom: 10px; padding-top: 0px;}
    .sub-text {font-size: 16px; color: #666; text-align: center; margin-bottom: 30px;}
    div[data-testid="stForm"] {border: 1px solid #ddd; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    div.stButton > button {width: 100%; background-color: #222; color: white; font-weight: bold; padding: 12px; border-radius: 8px; border: none;}
    div.stButton > button:hover {background-color: #444; color: white;}
    .info-box {background-color: #f1f3f5; border-left: 5px solid #222; color: #333; padding: 15px; border-radius: 4px; margin-top: 20px; font-size: 14px; line-height: 1.6;}
    </style>
    """, unsafe_allow_html=True)

# 3. 화면 구성
st.markdown('<div class="main-header">대성쎌틱 대리점 QR생성기</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">정보를 입력하면 <b>접속 가능한 주소</b>와 <b>QR코드</b>가 생성됩니다.</div>', unsafe_allow_html=True)

# 4. 입력 폼
with st.form("info_form"):
    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("상호명", placeholder="예: 대성쎌틱 대전서구")
    with col2:
        filename_input = st.text_input("파일 이름 (영문 권장)", placeholder="예: seogu_0425248577")
        st.caption("* 영문/숫자 권장, 중복되지 않게 고유하게 작성")

    phone_number = st.text_input("전화번호", placeholder="예: 010-1234-5678")
    price_url = st.text_input("단가표 링크 (선택)", placeholder="www.example.com")

    st.markdown("###")
    submitted = st.form_submit_button("주소 및 QR코드 생성하기")

# 5. 로직 실행
if submitted:
    # 1차 검증: 필수값 확인
    if not store_name or not phone_number:
        st.error("⚠️ 상호명과 전화번호는 필수입니다.")
        st.stop()
    if not filename_input:
        st.error("⚠️ 파일 이름을 입력해주세요.")
        st.stop()

    # 2차 검증: 데이터 세탁 및 유효성 검사
    save_name = sanitize_filename(filename_input)
    if not save_name:
        st.error("⚠️ 파일 이름에 사용할 수 없는 문자가 포함되어 있습니다. (영문/숫자 사용 권장)")
        st.stop()

    safe_store_name = sanitize_store_name(store_name)
    safe_phone_digits = sanitize_phone(phone_number)
    safe_price_url = normalize_http_url(price_url)

    if not safe_phone_digits:
        st.error("⚠️ 전화번호 형식이 올바르지 않습니다. 숫자를 포함해 입력해주세요.")
        st.stop()

    # 파일명 최종 확정
    full_filename = f"{save_name}.html"
    
    # 3. HTML 생성 (OG 태그 추가 및 보안 변수 적용)
    html_code = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="{safe_store_name}">
<meta property="og:description" content="친절하고 정확한 상담 도와드리겠습니다.">
<meta property="og:type" content="website">
<title>{safe_store_name}</title>
<style>
body {{font-family: 'Apple SD Gothic Neo', sans-serif; margin: 0; padding: 0; background-color: #f9f9f9; display: flex; flex-direction: column; align-items: center; min-height: 100vh;}}
.container {{width: 100%; max-width: 600px; background-color: #fff; padding: 50px 20px; box-sizing: border-box; text-align: center; border-bottom: 1px solid #eee;}}
h1 {{font-size: 26px; margin-bottom: 15px; font-weight: bold;}}
p {{font-size: 17px; color: #555; margin-bottom: 40px; line-height: 1.6;}}
.btn {{display: block; width: 100%; max-width: 320px; margin: 12px auto; padding: 16px 0; font-size: 17px; font-weight: bold; text-decoration: none; border-radius: 8px; background-color: #fff; color: #000; border: 2px solid #000; transition: background-color 0.2s;}}
.btn:hover {{background-color: #f0f0f0;}}
</style>
</head>
<body>
<div class="container">
<h1>{safe_store_name}</h1>
<p>친절하고 정확한 상담 도와드리겠습니다.<br>아래 버튼을 눌러주세요.</p>
<a href="tel:{safe_phone_digits}" class="btn">전화 상담 연결</a>
{f'<a href="{safe_price_url}" class="btn" target="_blank" rel="noopener noreferrer">단가표 보기</a>' if safe_price_url else ''}
</div>
</body>
</html>"""

    # 4. 깃허브 업로드
    try:
        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        repo = g.get_user().get_repo(REPO_NAME)

        # 파일 생성 또는 업데이트
        try:
            contents = repo.get_contents(full_filename)
            repo.update_file(contents.path, f"Update {full_filename}", html_code, contents.sha)
            status_msg = "업데이트(덮어쓰기) 완료"
        except:
            repo.create_file(full_filename, f"Create {full_filename}", html_code)
            status_msg = "신규 생성 완료"

        final_url = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/{full_filename}"
        
        st.success(f"✅ {status_msg}! 보안 검사를 통과했습니다.")

        # 결과 화면
        col_res1, col_res2 = st.columns([1.5, 1])
        
        with col_res1:
            st.markdown(f"### 생성된 주소")
            st.code(final_url, language="text")
            st.markdown(f"[바로가기 ({final_url})]({final_url})")
            
            st.markdown("""
            <div class="info-box">
            <b>잠시만 기다려주세요!</b><br>
            새로 만든 주소는 전 세계에 배포되는 데 <b>약 1~2분</b> 정도 소요됩니다.<br>
            그동안 옆의 <b>QR코드 이미지</b>를 다운로드하세요.
            </div>
            """, unsafe_allow_html=True)

        with col_res2:
            st.markdown("### QR코드")
            
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(final_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = BytesIO()
            img.save(buf)
            byte_im = buf.getvalue()
            
            st.image(byte_im, caption=f"{safe_store_name} QR", use_column_width=True)
            
            st.download_button(
                label="QR 이미지 저장",
                data=byte_im,
                file_name=f"QR_{save_name}.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(f"❌ 오류 발생! 에러 내용: {e}")
