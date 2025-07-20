import streamlit as st
import yt_dlp
import openai
import os
from googletrans import Translator
from gtts import gTTS

st.set_page_config(page_title="YouTube بصوت عربي", layout="centered")
st.title("🎬 مشاهدة فيديو YouTube مع التعليق الصوتي العربي")

openai_api_key = st.text_input("🔐 أدخل مفتاح OpenAI API", type="password")

youtube_url = st.text_input("📺 أدخل رابط فيديو YouTube (مسجّل)")

if youtube_url and openai_api_key and st.button("ابدأ"):
    with st.spinner("⏳ جاري معالجة الفيديو..."):
        audio_file = "audio.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        openai.api_key = openai_api_key
        with open(audio_file, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f)
        english_text = transcript["text"]

        translator = Translator()
        arabic_text = translator.translate(english_text, dest='ar').text

        tts = gTTS(text=arabic_text, lang='ar')
        voice_file = "voice.mp3"
        tts.save(voice_file)

        # عرض الفيديو
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[-1]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[-1]
        else:
            video_id = ""

        if video_id:
            st.video(f"https://www.youtube.com/watch?v={video_id}")
        
        st.audio(voice_file, format="audio/mp3")
        st.text_area("📜 النص العربي:", arabic_text, height=250)

        with open(voice_file, "rb") as f:
            st.download_button("📥 تحميل الصوت العربي", f, file_name="arabic_voice.mp3")

        os.remove(audio_file)
        os.remove(voice_file)
