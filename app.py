import streamlit as st
import yt_dlp
import openai
import os
from deep_translator import GoogleTranslator
from gtts import gTTS

# إعداد صفحة Streamlit
st.set_page_config(page_title="YouTube بصوت عربي", layout="centered")
st.title("🎬 مشاهدة فيديو YouTube مع التعليق الصوتي العربي")

# استخدام مفتاح OpenAI من secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# إدخال رابط فيديو YouTube
youtube_url = st.text_input("📺 أدخل رابط فيديو YouTube (يُفضّل أن يكون مسجّل وصوته واضح)")

if youtube_url and st.button("ابدأ"):
    with st.spinner("⏳ جارٍ تحميل الفيديو وتحويل الصوت إلى نص..."):
        try:
            # تحميل ملف الصوت فقط
            audio_file = "input_audio.webm"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_file,
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            # تحويل الصوت إلى نص باستخدام Whisper API الحديثة
            with open(audio_file, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            english_text = transcript.text

            # ترجمة النص إلى العربية
            arabic_text = GoogleTranslator(source='auto', target='ar').translate(english_text)

            # توليد صوت عربي باستخدام gTTS
            voice_file = "voice.mp3"
            tts = gTTS(text=arabic_text, lang='ar')
            tts.save(voice_file)

            # عرض فيديو YouTube داخل الصفحة
            video_id = ""
            if "v=" in youtube_url:
                video_id = youtube_url.split("v=")[-1]
            elif "youtu.be/" in youtube_url:
                video_id = youtube_url.split("youtu.be/")[-1]

            if video_id:
                st.video(f"https://www.youtube.com/watch?v={video_id}")

            # تشغيل الصوت المترجم
            st.audio(voice_file, format="audio/mp3")
            st.text_area("📜 الترجمة العربية:", arabic_text, height=250)

            with open(voice_file, "rb") as f:
                st.download_button("📥 تحميل الصوت العربي", f, file_name="arabic_voice.mp3")

            # تنظيف الملفات
            os.remove(audio_file)
            os.remove(voice_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء التنفيذ: {e}")
