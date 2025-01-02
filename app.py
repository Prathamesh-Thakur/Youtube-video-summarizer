import google.generativeai as genai
import streamlit as st
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import time

genai.configure(api_key=st.secrets['API_KEY'])
youtube_api_key = st.secrets['YOUTUBE_API_KEY']

model = genai.GenerativeModel(model_name='gemini-1.5-flash')

st.title("Youtube video summarizer")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.answers = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

url = st.chat_input("Enter a youtube video link:")

if url:
    video_id = url.split("v=")[1]

    video_info_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={youtube_api_key}"
    video_info_response = requests.get(video_info_url)
    video_info_data = video_info_response.json()

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    transcript_text = ""

    for i in range(len(transcript)):
        transcript_text += transcript[i]['text'] + " "

    video_title = video_info_data['items'][0]['snippet']['title']
    final_text = "Video title:" + video_title + "\n" + transcript_text

    prompt = final_text + """\nGiven the following youtube video title and transcript, generate a 
                                summary of no less than 500 characters and no more than 1000 characters.""" 

    with st.chat_message("user"):
        st.markdown(url)
    
    st.session_state.messages.append({"role": "user", "content": url})

    answer = video_title + "\n"
    
    response = model.generate_content(prompt, stream = True)
    for chunk in response:
        answer += chunk.text
    
    st.session_state.answers += answer + "\n"
    
    def stream_data():
        for word in answer.split():
            yield word + " "
            time.sleep(0.02)
    
    st.write_stream(stream_data)

    st.session_state.messages.append({"role": "assistant", "content": answer})

    st.download_button(label = "Download answers", data = st.session_state.answers, file_name = "Answers.txt")
