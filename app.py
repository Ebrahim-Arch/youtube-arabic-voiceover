import streamlit as st
import yt_dlp
import openai
import os
from deep_translator import GoogleTranslator
from gtts import gTTS

# إعداد واجهة التطبيق
st.set_page_config(page_title="YouTube بصوت عربي", layout="centered")
st.title("🎬 مشاهدة فيديو YouTube مع التعليق الصوتي العربي")

# استخدام مفتاح OpenAI من secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = openai_api_key

# إدخال رابط YouTube
youtube_url = st.text_input("📺 أدخل رابط فيديو YouTube (مسجّل)")

if youtube_url and st.button("ابدأ"):
    with st.spinner("⏳ جاري المعالجة..."):
        # تحميل الصوت من الفيديو
        audio_file = "audio.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # تحويل الصوت إلى نص عبر Whisper API
        with open(audio_file, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f)
        english_text = transcript["text"]

        # الترجمة إلى العربية
        arabic_text = GoogleTranslator(source='auto', target='ar').translate(english_text)

        # توليد الصوت العربي باستخدام gTTS
        voice_file = "voice.mp3"
        tts = gTTS(text=arabic_text, lang='ar')
        tts.save(voice_file)

        # استخراج video ID لعرض الفيديو داخل الصفحة
        video_id = ""
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[-1]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[-1]

        if video_id:
            st.video(f"https://www.youtube.com/watch?v={video_id}")

        # عرض الصوت والنص
        st.audio(voice_file, format="audio/mp3")
        st.text_area("📜 النص العربي:", arabic_text, height=250)

        # تحميل الصوت العربي
        with open(voice_file, "rb") as f:
            st.download_button("📥 تحميل الصوت العربي", f, file_name="arabic_voice.mp3")

        # تنظيف الملفات المؤقتة
        os.remove(audio_file)
        os.remove(voice_file)
