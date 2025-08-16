import streamlit as st
import subprocess
import os
import shutil

SUPPORTED_SITES = ["youtube.com", "youtu.be", "instagram.com", "twitter.com", "x.com"]
DOWNLOAD_DIR = "downloads"

def is_supported_url(url):
    return any(site in url for site in SUPPORTED_SITES)

def check_ffmpeg():
    """Check if ffmpeg is available in PATH."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except Exception:
        return False

def check_ytdlp():
    """Check if yt-dlp is available in PATH."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except Exception:
        return False

def extract_audio(url):
    """Extract audio using yt-dlp."""
    if not check_ytdlp():
        raise Exception("yt-dlp is not installed or not in PATH.")
    if not check_ffmpeg():
        raise Exception("ffmpeg is not installed or not in PATH.")

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    outtmpl = os.path.join(DOWNLOAD_DIR, f"audio_%(id)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", outtmpl,
        "--add-header", "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        url
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        for file in os.listdir(DOWNLOAD_DIR):
            if file.endswith(".mp3"):
                return os.path.join(DOWNLOAD_DIR, file)
        raise Exception("Audio file not found after download.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"yt-dlp error: {e.stderr}")

def clean_downloads():
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)


# ----------------- STREAMLIT UI -----------------
st.set_page_config(page_title="Audio Extractor", page_icon="🎵", layout="centered")
st.title("🎵 Social Media Audio Extractor")
st.write("Extract audio from YouTube, Instagram, and Twitter links.")

if not check_ytdlp():
    st.error("yt-dlp is not installed or not in PATH. Please install with 'pip install yt-dlp'.")
if not check_ffmpeg():
    st.error("ffmpeg is not installed or not in PATH. Add 'ffmpeg' to packages.txt if deploying.")

with st.form("audio_form"):
    url = st.text_input("Paste a YouTube, Instagram, or Twitter link:")
    submitted = st.form_submit_button("Extract Audio")

if submitted:
    clean_downloads()
    if not url or not is_supported_url(url):
        st.error("Please enter a valid YouTube, Instagram, or Twitter link.")
    elif not check_ytdlp() or not check_ffmpeg():
        st.error("yt-dlp or ffmpeg not available.")
    else:
        with st.spinner("Extracting audio..."):
            try:
                audio_path = extract_audio(url)
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                st.success("✅ Audio extracted successfully!")
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="⬇️ Download Audio",
                    data=audio_bytes,
                    file_name=os.path.basename(audio_path),
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"Failed to extract audio: {e}")

st.caption("Built with Streamlit & yt-dlp 🚀")
