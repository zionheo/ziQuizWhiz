import streamlit as st  
import datetime
import openai  
from openai import AzureOpenAI

api_key = None
if api_key is None or api_key =="":
    api_key = st.text_input("api key를 넣어주세요",type="password")

# Azure OpenAI 설정  
client = AzureOpenAI(
    azure_endpoint="https://zion-aoai.openai.azure.com/",
    api_key=api_key,
    api_version="2024-02-15-preview",
) 
col1,col2,col3 = st.columns([2,7,1])
with col1 :
    st.header("시온퀴즈쇼에 오신걸 환영함 ㅋ")
    if st.button("현재순위보기"):
        try:
            with open("quiz.txt", "r") as f:
                data = f.read()
            st.text_area("저장된 생년월일/이름 리스트", data)
        except FileNotFoundError:   
            st.warning("아직 저장된 데이터가 없습니다.")
with col2 :
    st.title("상식 퀴즈 게임")  
    st.write("틀릴 때까지 퀴즈를 맞추면 되요.")  

    # 초기화  
    if 'score' not in st.session_state:  
        st.session_state.score = 0  
    if 'question' not in st.session_state:  
        st.session_state.question = None  
    if 'answer' not in st.session_state:  
        st.session_state.answer = None  
    if 'game_over' not in st.session_state:  
        st.session_state.game_over = False  

    # 이름 입력
    birth = st.date_input("생일을 입력하세요.",min_value= datetime.date(2000,1,1))
    name = st.text_input("이름을 입력하세요:")

    st.write(f"하이루, {name} 게임을 시작하지...")  
    # 퀴즈 질문 생성 함수  
    def generate_quiz_question():  
        response = client.chat.completions.create(  
            model="gpt-4o",  
            messages=[  
                {"role": "system", "content": "너는 고등학생 수준의 상식 퀴즈를 내주는 ai야. 퀴즈 앞에 그 퀴즈의 주제를 [주제]로 표현해줘.한 문제만 내줘"},  
                {"role": "user", "content": "퀴즈를 내줘."}  
            ]  
        )  
        question = response.choices[0].message.content
        return question  

    # 첫 번째 질문 생성  
    if st.session_state.question is None and name:  
        st.session_state.question = generate_quiz_question()  

    # 퀴즈 출력  
    if st.session_state.game_over == False and name:  
        st.write(f"문제: {st.session_state.question}")  
        user_answer = st.text_input("정답을 입력하세요:")  

        if st.button("제출"):  
            # 정답 확인  
            response = client.chat.completions.create(  
                model="gpt-4o",  
                messages=[  
                    {"role": "system", "content": "너는 고등학생 수준의 상식 퀴즈의 정답을 채점하는 ai야.맞으면 Y, 틀리면 N이라고 답해줘."},  
                    {"role": "user", "content": f"질문:{st.session_state.question}\n사용자제출값: {user_answer}"}  
                ]  
            )
            yorn = response.choices[0].message.content.strip().lower()  

            if yorn == "y":  
                st.session_state.score += 1  
                st.success("정답입니다!")  
                st.session_state.question = generate_quiz_question() 
                st.rerun()
            else:  
                st.session_state.game_over = True
                response = client.chat.completions.create(  
                    model="gpt-4o",  
                    messages=[  
                        {"role": "system", "content": "아래 질문에 대한 답을 알려줘."},  
                        {"role": "user", "content": f"질문:{st.session_state.question}\n사용자제출값: {user_answer}"}  
                    ]  
                )
                st.warning("틀렸어요")
                response.choices[0].message.content.strip().lower()
                st.write(response.choices[0].message.content.strip().lower())
                
                if birth and name:
                    with open("quiz.txt", "a") as f:
                        f.write(f"{birth} - {name} - {st.session_state.score}\n")
                    
                else:
                    st.warning("생년월일과 이름을 입력하세요.")


with col3:

# 결과 출력  
    if st.session_state.game_over == True:  
        st.write(f"게임 끝남! {name}님의 점수: {st.session_state.score}점")
        st.session_state.score = 0
        st.session_state.game_over = False
    else:  
        if name:
            st.write(f"현재 점수: {st.session_state.score}점")  
