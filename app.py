import streamlit as st
import subprocess
import os
import shutil
import sys

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
    """
    Extract audio from the given URL using yt-dlp.
    Returns the path to the audio file or raises an Exception.
    """
    if not check_ytdlp():
        raise Exception("yt-dlp is not installed or not in PATH. Please install yt-dlp and ensure it's in your PATH.")
    if not check_ffmpeg():
        raise Exception("ffmpeg is not installed or not in PATH. Please install ffmpeg and ensure it's in your PATH.")
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    # Generate a unique filename
    outtmpl = os.path.join(DOWNLOAD_DIR, f"audio_%(id)s.%(ext)s")
    # yt-dlp command to extract best audio
    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", outtmpl,
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Find the output file
        for file in os.listdir(DOWNLOAD_DIR):
            if file.endswith(".mp3"):
                return os.path.join(DOWNLOAD_DIR, file)
        raise Exception("Audio file not found after download.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"yt-dlp error: {e.stderr}")

def clean_downloads():
    """Remove all files in the downloads directory."""
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)


st.set_page_config(page_title="Audio Extractor", page_icon="🎵", layout="centered")
st.title("🎵 Social Media Audio Extractor")
st.write("Extract audio from YouTube, Instagram, and Twitter links.")

if not check_ytdlp():
    st.error("yt-dlp is not installed or not in PATH. Please install yt-dlp using 'pip install yt-dlp' and ensure it's in your PATH.")
if not check_ffmpeg():
    st.error("ffmpeg is not installed or not in PATH. Please install ffmpeg and ensure it's in your PATH. [Download ffmpeg](https://ffmpeg.org/download.html)")


with st.form("audio_form"):
    url = st.text_input("Paste a YouTube, Instagram, or Twitter link:")
    submitted = st.form_submit_button("Extract Audio")


if submitted:
    clean_downloads()
    if not url or not is_supported_url(url):
        st.error("Please enter a valid YouTube, Instagram, or Twitter link.")
    elif not check_ytdlp() or not check_ffmpeg():
        st.error("Cannot extract audio: yt-dlp or ffmpeg is not available. See above for installation instructions.")
    else:
        with st.spinner("Extracting audio, please wait..."):
            try:
                audio_path = extract_audio(url)
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                st.success("Audio extracted successfully!")
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="Download Audio",
                    data=audio_bytes,
                    file_name=os.path.basename(audio_path),
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"Failed to extract audio: {e}")

st.caption("Built with Streamlit & yt-dlp. ")
