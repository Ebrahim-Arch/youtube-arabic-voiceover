import streamlit as st
import yt_dlp
import openai
import os
from deep_translator import GoogleTranslator
from gtts import gTTS

# إعداد صفحة Streamlit
st.set_page_config(page_title="YouTube بصوت عربي", layout="centered")
st.title("🎬 مشاهدة فيديو YouTube مع التعليق الصوتي العربي")

# مفتاح OpenAI من secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# إدخال رابط فيديو YouTube
youtube_url = st.text_input("📺 أدخل رابط فيديو YouTube (يُفضّل أن يكون قصيرًا وواضح الصوت)")

# عند الضغط على زر التنفيذ
if youtube_url and st.button("ابدأ"):
    with st.spinner("⏳ جاري تحليل الفيديو وإنشاء الصوت العربي..."):
        try:
            # تحميل الصوت من الفيديو بدون تحويل
            audio_file = "input_audio.webm"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_file,
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            # تحويل الصوت إلى نص باستخدام Whisper API
            with open(audio_file, "rb") as f:
                transcript = openai.Audio.transcribe("whisper-1", f)
            english_text = transcript["text"]

            # الترجمة إلى العربية
            arabic_text = GoogleTranslator(source='auto', target='ar').translate(english_text)

            # توليد الصوت العربي
            voice_file = "voice.mp3"
            tts = gTTS(text=arabic_text, lang='ar')
            tts.save(voice_file)

            # استخراج الفيديو ID لعرضه داخل الصفحة
            video_id = ""
            if "v=" in youtube_url:
                video_id = youtube_url.split("v=")[-1]
            elif "youtu.be/" in youtube_url:
                video_id = youtube_url.split("youtu.be/")[-1]

            if video_id:
                st.video(f"https://www.youtube.com/watch?v={video_id}")

            # عرض الصوت العربي والنص
            st.audio(voice_file, format="audio/mp3")
            st.text_area("📜 النص المترجم إلى العربية:", arabic_text, height=250)

            with open(voice_file, "rb") as f:
                st.download_button("📥 تحميل الصوت العربي", f, file_name="arabic_voice.mp3")

            os.remove(audio_file)
            os.remove(voice_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء تنفيذ العملية: {str(e)}")
