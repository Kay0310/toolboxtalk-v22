import streamlit as st
import datetime
import pytz

# --- 세션 초기화 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.company = ""
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.room_code = ""
    st.session_state.rooms = {}

kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.datetime.now(kst)
today_kst = now_kst.date()
time_kst = now_kst.strftime("%H:%M")

# --- 로그인 / 회의 시작 ---
if not st.session_state.logged_in:
    st.title("Toolbox Talk 회의록 시작")
    company = st.text_input("회사명", placeholder="예: HealSE Co., Ltd.")
    role = st.radio("역할", ["관리자", "팀원"])
    name = st.text_input("이름")

    if role == "관리자":
        code = st.text_input("회의 코드 (예: 건설팀-0511)")
        team_list = st.text_area("팀원 목록 (쉼표로 구분)", "김강윤,이민우,박지현")
        if st.button("회의 시작") and code and team_list:
            st.session_state.rooms[code] = {
                "company": company,
                "admin": name,
                "members": [n.strip() for n in team_list.split(",")],
                "attendees": [],
                "confirmations": [],
                "discussion": [],
                "tasks": [],
                "info": {},
                "additional": ""
            }
            st.session_state.room_code = code
            st.session_state.company = company
            st.session_state.username = name
            st.session_state.role = role
            st.session_state.logged_in = True
    else:
        code = st.text_input("참여할 회의 코드")
        if st.button("입장") and name and code:
            if code in st.session_state.rooms and name in st.session_state.rooms[code]["members"]:
                st.session_state.room_code = code
                st.session_state.username = name
                st.session_state.role = role
                st.session_state.company = st.session_state.rooms[code]["company"]
                st.session_state.logged_in = True
            else:
                st.error("회의 코드가 없거나 이름이 등록되지 않았습니다.")
    st.stop()

# --- 회의방 메인 ---
code = st.session_state.room_code
room = st.session_state.rooms[code]
user = st.session_state.username
is_admin = st.session_state.role == "관리자"

if user not in room["attendees"]:
    room["attendees"].append(user)

st.title(f"Toolbox Talk 회의록 - [{code}]")

# 1. 회의 정보
st.header("1️⃣ 회의 정보")
if is_admin:
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", today_kst)
        place = st.text_input("장소", "현장 A")
    with col2:
        time = st.text_input("시간", time_kst)
        task = st.text_input("작업 내용", "고소작업")
    room["info"] = {"date": str(date), "place": place, "time": time, "task": task}
else:
    info = room.get("info", {})
    st.markdown(f"- 날짜: {info.get('date')}  ⏱ 시간: {info.get('time')}")
    st.markdown(f"- 장소: {info.get('place')}   작업: {info.get('task')}")

# 2. 참석자
st.header("2️⃣ 참석자 명단")
st.markdown(", ".join(room["attendees"]))

# 3. 논의 내용
st.header("3️⃣ 논의 내용")
if is_admin:
    r = st.text_input("위험요소", key="r")
    m = st.text_input("안전대책", key="m")
    if st.button(" 논의 내용 추가") and r and m:
        room["discussion"].append((r, m))
else:
    for idx, (r, m) in enumerate(room["discussion"]):
        st.markdown(f"{idx+1}. **{r}** → {m}")

# 4. 추가 논의
st.header("4️⃣ 추가 논의 사항")
if is_admin:
    room["additional"] = st.text_area("기타 사항 입력", value=room.get("additional", ""))
else:
    st.markdown(room.get("additional", ""))

# 5. 결정사항
st.header("5️⃣ 결정사항 및 조치")
if is_admin:
    col1, col2, col3 = st.columns(3)
    p = col1.text_input("담당자", key="p")
    r = col2.text_input("업무/역할", key="r2")
    d = col3.date_input("완료예정일", today_kst)
    if st.button(" 조치 추가") and p and r:
        room["tasks"].append((p, r, d))
else:
    for p, r, d in room["tasks"]:
        st.markdown(f"- {p}: {r} (예정: {d})")

# 6. 서명
st.header("6️⃣ 회의록 확인 및 서명")
if user not in room["confirmations"]:
    if st.button(" 회의 내용 확인"):
        room["confirmations"].append(user)
        st.success("확인 저장되었습니다.")
else:
    st.info("이미 확인하셨습니다.")

# 관리자 현황
if is_admin:
    st.markdown(f"서명 완료: {len(room['confirmations'])} / {len(room['members'])}")
    for name in room["members"]:
        mark = "" if name in room["confirmations"] else "❌"
        st.markdown(f"- {name} {mark}")

# 인쇄용 미리보기
with st.expander("🖨 인쇄용 회의 미리보기", expanded=True):
    html = f'''<div style="font-family: 'NanumGothic', sans-serif; font-size:14px; padding:30px; line-height:1.8;">
    <h2 style="text-align:center; font-size:20pt; margin-bottom:4px;">
        Toolbox Talk 회의록 - [{room["team"]}]
    </h2>
    <p style="text-align:center; font-size:12pt; margin-top:0;">회사명: {room["company"]}</p>
    <p><b> 날짜:</b> {room["info"]["date"]} &nbsp;&nbsp; <b> 시간:</b> {room["info"]["time"]}</p>
    <p><b> 장소:</b> {room["info"]["place"]} &nbsp;&nbsp; <b> 작업:</b> {room["info"]["task"]}</p>
    <p><b> 리더:</b> {room["admin"]}</p>

    <h3 style="margin-top:30px;"> 참석자</h3>
    <ul>{''.join([f"<li>{name}</li>" for name in room["attendees"]])}</ul>

    <h3 style="margin-top:30px;"> 논의 내용</h3>
    <ol>{''.join([f"<li><b>{r}</b> → {m}</li>" for r, m in room["discussion"]])}</ol>

    <h3 style="margin-top:30px;"> 추가 논의</h3>
    <p>{room["additional"]}</p>

    <h3 style="margin-top:30px;"> 결정사항 및 조치</h3>
    <ul>{''.join([f"<li>{p}: {r} (예정일: {d})</li>" for p, r, d in room["tasks"]])}</ul>

    <h3 style="margin-top:30px;"> 확인자</h3>
    <ul>{''.join([f"<li>{n} (확인 완료)</li>" for n in room["confirmations"]])}</ul>

    <hr style="margin-top:40px;">
    <p style="text-align:right; font-size:10pt;">App. support by HealSE Co., Ltd.</p>
</div>
'''

# height 충분히 크게 설정
'''

html = f'''
    <div style="font-family:sans-serif; line-height:1.6; font-size:16px; padding:20px;">
        <h2 style="text-align:center; font-size:22px;">Toolbox Talk 회의록 - [{code}]</h2>
        <p style="text-align:center; font-size:14px;">회사명: {room["company"]}</p>
        <p><b>날짜:</b> {room["info"].get("date")} &nbsp; <b>시간:</b> {room["info"].get("time")}</p>
        <p><b>장소:</b> {room["info"].get("place")} &nbsp; <b>작업:</b> {room["info"].get("task")}</p>
        <p><b>리더:</b> {room["admin"]}</p>

        <h4> 참석자</h4>
        <ul>{"".join(f"<li>{n}</li>" for n in room["attendees"])}</ul>

        <h4> 논의 내용</h4>
        <ol>{"".join(f"<li><b>{r}</b> → {m}</li>" for r, m in room["discussion"])}</ol>

        <h4> 추가 논의</h4>
        <p>{room["additional"]}</p>

        <h4> 결정사항 및 조치</h4>
        <ul>{"".join(f"<li>{p}: {r} (예정일: {d})</li>" for p, r, d in room["tasks"])}</ul>

        <h4> 확인자</h4>
        <ul>{"".join(f"<li>{n} (확인 완료)</li>" for n in room["confirmations"])}</ul>

        <hr>
        <p style="text-align:right; font-size:10px;">App. support by HealSE Co., Ltd.</p>
    </div>
    '''
    st.components.v1.html(html, height=3000, scrolling=True)
'''