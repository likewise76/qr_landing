import streamlit as st
import re
import qrcode
from PIL import Image
from io import BytesIO
from github import Github

# --- [설정] 지역장님 정보 ---
GITHUB_USERNAME = "likewise76"   
REPO_NAME = "qr_address"         
# ---------------------------

# 1. 페이지 설정 (탭 제목 변경, 아이콘 제거)
st.set_page_config(page_title="대성쎌틱 대리점 QR생성기", layout="centered")

# 2. 스타일 설정 (기존과 동일하게 메뉴/버튼 숨김 유지)
st.markdown("""
    <style>
    /* 전체 배경 흰색 */
    .stApp {background-color: #ffffff;}
    
    /* 상단 헤더, 햄버거 메뉴, 푸터, 관리 버튼 숨기기 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
    
    /* 메인 타이틀 스타일 */
    .main-header {
        font-size: 28px; 
        font-weight: 700; 
        color: #111; 
        text-align: center; 
        margin-bottom: 10px; 
        padding-top: 0px; 
    }
    
    /* 서브 텍스트 */
    .sub-text {
        font-size: 16px; 
        color: #666; 
        text-align: center; 
        margin-bottom: 30px;
    }
    
    /* 입력창 디자인 */
    div[data-testid="stForm"] {
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* 버튼 스타일 */
    div.stButton > button {
        width: 100%; 
        background-color: #222; 
        color: white; 
        font-weight: bold; 
        padding: 12px; 
        border-radius: 8px; 
        border: none;
    }
    div.stButton > button:hover {
        background-color: #444; 
        color: white;
    }
    
    /* 안내 박스 스타일 */
    .info-box {
        background-color: #f1f3f5; 
        border-left: 5px solid #222;
        color: #333; 
        padding: 15px; 
        border-radius: 4px; 
        margin-top: 20px; 
        font-size: 14px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 화면 구성 (이모티콘 제거, 타이틀 수정)
st.markdown('<div class="main-header">대성쎌틱 대리점 QR생성기</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">정보를 입력하면 <b>접속 가능한 주소</b>와 <b>QR코드</b>가 생성됩니다.</div>', unsafe_allow_html=True)

# 4. 입력 폼
with st.form("info_form"):
    col1, col2 = st.columns(2)
    with col1:
        # [수정] 예시 변경
        store_name = st.text_input("상호명", placeholder="예: 대성쎌틱 대전서구")
    with col2:
        # [수정] 안내 문구 및 예시 변경
        filename_input = st.text_input("파일 이름 (영문 권장)", placeholder="예: seogu_0425248577")
        st.caption("* 가급적 '영문' 사용 권장, 다른 대리점과 겹치지 않게 고유하게 작성.\n* 예: seogu_0425248577")

    phone_number = st.text_input("전화번호", placeholder="예: 010-1234-5678")
    price_url = st.text_input("단가표 링크 (선택)", placeholder="http://...")

    st.markdown("###")
    # [수정] 버튼 텍스트에서 이모티콘 제거
    submitted = st.form_submit_button("주소 및 QR코드 생성하기")

# 5. 로직 실행
if submitted:
    if not store_name or not phone_number:
        st.error("상호명과 전화번호는 필수입니다.")
    elif not filename_input:
        st.error("파일 이름을 입력해주세요.")
    else:
        # 파일명 정리
        save_name = re.sub(r'[^a-zA-Z0-9_-]', '', filename_input)
        full_filename = f"{save_name}.html"

        # HTML 내용
        html_code = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{store_name}</title>
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
<h1>{store_name}</h1>
<p>친절하고 정확한 상담 도와드리겠습니다.<br>아래 버튼을 눌러주세요.</p>
<a href="tel:{phone_number}" class="btn">전화 상담 연결</a>
{'<a href="' + price_url + '" class="btn" target="_blank">단가표 보기</a>' if price_url else ''}
</div>
</body>
</html>"""

        # 깃허브 업로드
        try:
            token = st.secrets["GITHUB_TOKEN"]
            g = Github(token)
            repo = g.get_user().get_repo(REPO_NAME)

            try:
                contents = repo.get_contents(full_filename)
                repo.update_file(contents.path, f"Update {full_filename}", html_code, contents.sha)
            except:
                repo.create_file(full_filename, f"Create {full_filename}", html_code)

            final_url = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/{full_filename}"
            
            # [수정] 성공 메시지 이모티콘 제거
            st.success("생성이 완료되었습니다!")

            # 결과 화면
            col_res1, col_res2 = st.columns([1.5, 1])
            
            with col_res1:
                # [수정] 제목 이모티콘 제거
                st.markdown(f"### 생성된 주소")
                st.code(final_url, language="text")
                st.markdown(f"[바로가기 ({final_url})]({final_url})")
                
                # [수정] 안내 박스 이모티콘 제거
                st.markdown("""
                <div class="info-box">
                <b>잠시만 기다려주세요!</b><br>
                새로 만든 주소는 서버반영에 <b>약 1~2분</b> 정도 소요됩니다.<br>
                그동안 옆의 <b>QR코드 이미지</b>를 다운로드하세요.
                </div>
                """, unsafe_allow_html=True)

            with col_res2:
                # [수정] 제목 이모티콘 제거
                st.markdown("### QR코드")
                
                qr = qrcode.QRCode(version=1, box_size=10, border=2)
                qr.add_data(final_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                buf = BytesIO()
                img.save(buf)
                byte_im = buf.getvalue()
                
                st.image(byte_im, caption=f"{store_name} QR", use_column_width=True)
                
                # [수정] 버튼 텍스트 이모티콘 제거
                st.download_button(
                    label="QR 이미지 저장",
                    data=byte_im,
                    file_name=f"QR_{save_name}.png",
                    mime="image/png"
                )

        except Exception as e:
            st.error(f"오류 발생! 에러 내용: {e}")
