"""
OpenLens - Minimalist AI Video Generation Portal
A raw transparency API pass-through for AI video generation.

Features:
- Pure pass-through: no content filtering, no safety middleware
- Manual API config with LocalStorage persistence  
- OpenAI-style /v1/video/generations support
- Auto-polling for async video generation
- HTML5 video player with download button
"""

import streamlit as st
import requests
import time
import json
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="OpenLens",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark minimalist theme
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background: #0a0a0a;
        color: #e0e0e0;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: #1a1a1a;
        border: 1px solid #333;
        color: #fff;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background: #1a1a1a;
        border: 1px solid #333;
        color: #fff;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        font-weight: 600;
    }
    
    /* Video container */
    .video-container {
        background: #000;
        border-radius: 12px;
        padding: 16px;
        margin-top: 16px;
    }
    
    /* Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    .subtitle {
        color: #666;
        font-size: 0.9rem;
        margin-top: -10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE MANAGEMENT
# ============================================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Initialize other session variables
if 'api_url' not in st.session_state:
    st.session_state.api_url = ""
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'task_status' not in st.session_state:
    st.session_state.task_status = None
if 'video_url' not in st.session_state:
    st.session_state.video_url = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'uploaded_image_url' not in st.session_state:
    st.session_state.uploaded_image_url = None
if 'text_api_url' not in st.session_state:
    st.session_state.text_api_url = ""
if 'text_api_key' not in st.session_state:
    st.session_state.text_api_key = ""
if 'text_model' not in st.session_state:
    st.session_state.text_model = ""
if 'refined_prompt' not in st.session_state:
    st.session_state.refined_prompt = ""

# ============================================================
# AGE VERIFICATION PAGE (if not authenticated)
# ============================================================
if not st.session_state.authenticated:
    st.markdown("""
    <style>
    .age-container {
        max-width: 600px;
        margin: 80px auto;
        padding: 50px;
        background: #1a1a1a;
        border: 2px solid #667eea;
        border-radius: 20px;
        text-align: center;
    }
    .age-title {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }
    .age-text {
        color: #ccc;
        font-size: 16px;
        line-height: 2.2;
        margin-bottom: 30px;
    }
    .age-warning {
        color: #ef4444;
        font-size: 14px;
        padding: 15px;
        background: rgba(239, 68, 68, 0.1);
        border-radius: 8px;
        margin-top: 20px;
    }
    </style>
    
    <div class="age-container">
        <div class="age-title">🎬 OpenLens</div>
        <div class="age-text">
            <strong>Age Verification Required</strong><br><br>
            This is a <strong>transparent AI video generation gateway</strong>.<br><br>
            Please confirm all of the following:
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Checkboxes for confirmation
    col1, col2, col3 = st.columns(3)
    with col1:
        check1 = st.checkbox("✅ I am 18+ years old")
    with col2:
        check2 = st.checkbox("✅ I will use legally")
    with col3:
        check3 = st.checkbox("✅ I accept responsibility")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Enter button - only enabled when all checked
    if check1 and check2 and check3:
        if st.button("✅ Enter OpenLens", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.rerun()
    else:
        st.button("✅ Enter OpenLens", disabled=True, use_container_width=True)
        st.info("👆 Please check all boxes above to enter")
    
    st.markdown("---")
    st.markdown("""
    <div class="age-warning" style='text-align:center;'>
        ⚠️ Illegal or harmful content generation is strictly prohibited
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# ============================================================
# MAIN APP - AUTHENTICATED
# ============================================================
    st.session_state.api_key = ""
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'task_status' not in st.session_state:
    st.session_state.task_status = None
if 'video_url' not in st.session_state:
    st.session_state.video_url = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'uploaded_image_url' not in st.session_state:
    st.session_state.uploaded_image_url = None

# Text API config (for prompt refinement)
if 'text_api_url' not in st.session_state:
    st.session_state.text_api_url = ""
if 'text_api_key' not in st.session_state:
    st.session_state.text_api_key = ""
if 'text_model' not in st.session_state:
    st.session_state.text_model = ""
if 'refined_prompt' not in st.session_state:
    st.session_state.refined_prompt = ""

# ============================================================
# HELPER FUNCTIONS
# ============================================================

# System prompt for prompt refinement
REFINER_SYSTEM_PROMPT = """You are a top-tier AI video director. Your task is to transform the user's raw description into a professional, cinematic video prompt.

Requirements:
- Enhance with visual details: lighting, camera angles, color grading, atmosphere
- Add motion dynamics: movements, transitions, physics-based animations
- Include technical quality terms: high quality, detailed, 4K, cinematic
- Emphasize emotional tone and mood
- Keep it concise but vivid (50-150 words)
- Output ONLY the refined prompt, NO explanations, NO meta-commentary"""

def refine_prompt(text_api_url, text_api_key, text_model, user_prompt, image_url=None):
    """
    Call Text API to refine the prompt.
    Supports both text-only and vision (image-to-prompt) models.
    Returns the refined prompt or None on failure.
    """
    headers = {
        "Authorization": "Bearer " + text_api_key,
        "Content-Type": "application/json"
    }
    
    # Build messages
    if image_url:
        # Vision mode - send image URL with prompt
        messages = [
            {
                "role": "system",
                "content": REFINER_SYSTEM_PROMPT + "\n\nThe user has provided an image. Analyze the image and create a video prompt that captures its essence with dynamic motion."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    },
                    {
                        "type": "text",
                        "text": "Original description: " + user_prompt
                    }
                ]
            }
        ]
        log_message("Using Vision mode with image: %s" % image_url)
    else:
        # Text-only mode
        messages = [
            {
                "role": "system",
                "content": REFINER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    
    # Build payload - support both OpenAI-style and custom APIs
    payload = {
        "model": text_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    # Try chat/completions first, then responses API
    endpoints = [
        "%s/chat/completions" % text_api_url,
        "%s/responses" % text_api_url
    ]
    
    for endpoint in endpoints:
        try:
            log_message("Calling Text API: %s" % endpoint)
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Handle chat/completions format
                if "choices" in data:
                    content = data["choices"][0]["message"]["content"]
                    log_message("Refine success (chat): %s" % content[:100])
                    return content
                # Handle responses API format
                elif "output" in data:
                    content = data["output"][0]["content"][0]["text"]
                    log_message("Refine success (responses): %s" % content[:100])
                    return content
            else:
                log_message("Text API error %d: %s" % (resp.status_code, resp.text[:200]))
                
        except Exception as e:
            log_message("Text API exception: %s" % str(e))
            continue
    
    return None

def upload_to_catbox(file_data, filename):
    """
    Upload image to catbox.moe anonymous file hosting.
    Returns the public URL or None on failure.
    """
    try:
        files = {
            'reqtype': (None, 'fileupload'),
            'time': (None, '1h'),  # 1 hour expiration for anonymous
            'fileToUpload': (filename, file_data, 'image/' + filename.split('.')[-1])
        }
        
        log_message("Uploading to catbox.moe: %s" % filename)
        resp = requests.post('https://catbox.moe/user/api.php', files=files, timeout=60)
        
        if resp.status_code == 200 and resp.text.strip().startswith('http'):
            url = resp.text.strip()
            log_message("Upload success: %s" % url)
            return url
        else:
            log_message("Upload failed: %s" % resp.text[:200])
            return None
    except Exception as e:
        log_message("Upload exception: %s" % str(e))
        return None

def upload_to_tmpfiles(file_data, filename):
    """
    Upload image to tmpfiles.org (alternative)
    """
    try:
        files = {
            'file': (filename, file_data, 'image/' + filename.split('.')[-1])
        }
        resp = requests.post('https://tmpfiles.org/api/v1/upload', files=files, timeout=60)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success') and data.get('data'):
                url = data['data']['url']
                log_message("Upload to tmpfiles success: %s" % url)
                return url
        log_message("tmpfiles upload failed: %s" % resp.text[:200])
        return None
    except Exception as e:
        log_message("tmpfiles upload exception: %s" % str(e))
        return None

def log_message(msg):
    """Add timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = "[%s] %s" % (timestamp, msg)
    st.session_state.logs.append(log_entry)
    # Keep only last 50 logs
    if len(st.session_state.logs) > 50:
        st.session_state.logs = st.session_state.logs[-50:]

def submit_video_task(api_url, api_key, prompt, negative_prompt, 
                     resolution="720p", duration=5, **extra_params):
    """Submit video generation task to API"""
    
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }
    
    # Build payload - passthrough all parameters
    payload = {
        "model": extra_params.get("model", "video/wan2.6-i2v"),
        "input": {
            "prompt": prompt,
        }
    }
    
    # Add optional fields
    if negative_prompt:
        payload["input"]["negative_prompt"] = negative_prompt
    
    if "img_url" in extra_params and extra_params["img_url"]:
        payload["input"]["img_url"] = extra_params["img_url"]
    
    if "reference_urls" in extra_params:
        payload["input"]["reference_urls"] = extra_params["reference_urls"]
    
    # Parameters
    payload["parameters"] = {
        "size": resolution,
        "duration": duration,
    }
    
    if "seed" in extra_params and extra_params["seed"]:
        payload["parameters"]["seed"] = extra_params["seed"]
    
    if "watermark" in extra_params:
        payload["parameters"]["watermark"] = extra_params["watermark"]
    
    if "prompt_extend" in extra_params:
        payload["parameters"]["prompt_extend"] = extra_params["prompt_extend"]
    
    log_message("Submitting to: %s/video/generations" % api_url)
    log_message("Payload: %s" % json.dumps(payload, indent=2, ensure_ascii=False)[:500])
    
    try:
        resp = requests.post(
            "%s/video/generations" % api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            log_message("Task submitted: %s" % data.get('task_id'))
            log_message("Status: %s | Cost: $%s" % (data.get('status'), data.get('estimated_cost', 'N/A')))
            return data
        else:
            error_msg = "HTTP %d: %s" % (resp.status_code, resp.text[:200])
            log_message("Error: %s" % error_msg)
            return {"error": error_msg}
            
    except Exception as e:
        log_message("Exception: %s" % str(e))
        return {"error": str(e)}

def poll_task_status(api_url, api_key, task_id, max_attempts=120):
    """Poll task status until complete or failed"""
    
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_attempts):
        try:
            resp = requests.get(
                "%s/video/generations/%s" % (api_url, task_id),
                headers=headers,
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status", "UNKNOWN")
                progress = data.get("progress_percent", 0)
                
                st.session_state.task_status = status
                st.session_state.progress = progress
                
                log_message("Polling #%d: %s (%d%%)" % (attempt+1, status, progress))
                
                if status == "SUCCEED":
                    video_url = data.get("videos", [{}])[0].get("video_url")
                    st.session_state.video_url = video_url
                    log_message("SUCCESS! Video ready: %s" % video_url[:80])
                    return data
                    
                elif status == "FAILED":
                    log_message("FAILED: %s" % data.get('error', 'Unknown error'))
                    return data
                    
                # Wait before next poll
                time.sleep(5)
                
            else:
                log_message("Poll error HTTP %d" % resp.status_code)
                time.sleep(5)
                
        except Exception as e:
            log_message("Poll exception: %s" % str(e))
            time.sleep(5)
    
    return {"error": "Max polling attempts reached"}

# ============================================================
# MAIN UI
# ============================================================

# Header
st.markdown('<p class="main-header">🎬 OpenLens</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Minimalist AI Video Generation Portal | Raw Transparency Pass-through</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================
# SIDEBAR - API CONFIG
# ============================================================
with st.sidebar:
    st.header("⚙️ API Configuration")
    
    api_url_input = st.text_input(
        "API Base URL",
        value=st.session_state.api_url,
        placeholder="https://api.onlypixai.com/v1",
        help="The base URL of your video generation API"
    )
    
    api_key_input = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-px-...",
        help="Your API key for authentication"
    )
    
    # Save to session state
    if api_url_input != st.session_state.api_url:
        st.session_state.api_url = api_url_input
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
    
    st.markdown("---")
    st.markdown("**Note:** API URL and Key persist during this session.")
    
    # ============================================================
    # Text API Config (for Prompt Refinement)
    # ============================================================
    st.markdown("---")
    st.header("✏️ Text API (Prompt Refinement)")
    
    text_api_url_input = st.text_input(
        "Text API URL",
        value=st.session_state.text_api_url,
        placeholder="https://api.openai.com/v1",
        help="Base URL for text/chat API (e.g., OpenAI, OnlyPixAI, Ollama)"
    )
    
    text_api_key_input = st.text_input(
        "Text API Key",
        value=st.session_state.text_api_key,
        type="password",
        placeholder="sk-...",
        help="API key for text generation"
    )
    
    text_model_input = st.text_input(
        "Text Model ID",
        value=st.session_state.text_model,
        placeholder="gpt-4o, deepseek/deepseek-v3, etc.",
        help="Model ID for prompt refinement"
    )
    
    # Save to session state
    if text_api_url_input != st.session_state.text_api_url:
        st.session_state.text_api_url = text_api_url_input
    if text_api_key_input != st.session_state.text_api_key:
        st.session_state.text_api_key = text_api_key_input
    if text_model_input != st.session_state.text_model:
        st.session_state.text_model = text_model_input
    
    st.markdown("---")
    st.markdown("### API Format")
    st.code("""
POST /v1/video/generations
{
  "model": "video/wan2.6-i2v",
  "input": {
    "prompt": "...",
    "negative_prompt": "..."
  },
  "parameters": {
    "size": "720p",
    "duration": 5
  }
}
    """, language="json")
    
    # Logout button
    st.markdown("---")
    if st.button("🚪 Exit / Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ============================================================
# MAIN CONTENT
# ============================================================

# Create two columns
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Generate Video")
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["video/wan2.6-i2v", "video/wan2.6-t2v", "video/wan2.6-v2v"],
        help="Select video generation model"
    )
    
    # Prompt input
    prompt = st.text_area(
        "Prompt",
        height=120,
        value=st.session_state.refined_prompt or "",
        placeholder="Describe the video you want to generate...",
        help="Detailed description of the desired video"
    )
    
    # ============================================================
    # Prompt Refinement Controls
    # ============================================================
    col_prompt1, col_prompt2 = st.columns([3, 1])
    
    with col_prompt1:
        # Auto-refine & generate checkbox
        auto_refine = st.checkbox(
            "🔗 Auto-optimize & Generate",
            value=False,
            help="Automatically refine prompt before generating video"
        )
    
    with col_prompt2:
        # Optimize button
        optimize_btn = st.button(
            "✨ Optimize Prompt",
            use_container_width=True,
            help="Use LLM to enhance your prompt"
        )
    
    # Handle optimize button click
    if optimize_btn:
        if not st.session_state.text_api_url:
            st.error("❌ Please configure Text API in sidebar")
        elif not st.session_state.text_api_key:
            st.error("❌ Please enter Text API Key in sidebar")
        elif not st.session_state.text_model:
            st.error("❌ Please enter Text Model ID in sidebar")
        elif not prompt:
            st.error("❌ Please enter a prompt to optimize")
        else:
            with st.spinner("✨ Optimizing prompt with LLM..."):
                # Get image URL if available
                current_img_url = img_url if model == "video/wan2.6-i2v" and img_url else None
                
                refined = refine_prompt(
                    st.session_state.text_api_url,
                    st.session_state.text_api_key,
                    st.session_state.text_model,
                    prompt,
                    current_img_url
                )
                
                if refined:
                    st.session_state.refined_prompt = refined
                    st.success("✅ Prompt optimized!")
                    st.text_area("Refined Prompt", value=refined, height=100, key="refined_display")
                    st.rerun()
                else:
                    st.error("❌ Failed to optimize prompt")
    
    # Negative prompt
    negative_prompt = st.text_area(
        "Negative Prompt (optional)",
        height=60,
        placeholder="What to avoid in the video...",
        help="Things to exclude from the video"
    )
    
    # Advanced options
    with st.expander("⚡ Advanced Options"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            resolution = st.selectbox(
                "Resolution",
                ["720p", "1080p", "1280*720", "1920*1080"],
                index=0
            )
            duration = st.selectbox(
                "Duration",
                [5, 10, 15],
                index=0
            )
        
        with col_b:
            seed = st.text_input("Seed (optional)", placeholder="Random if empty")
            watermark = st.checkbox("Add Watermark", value=False)
            prompt_extend = st.checkbox("Smart Prompt Extend", value=True)
    
    # Image Upload for I2V (if needed)
    img_url = ""
    if model == "video/wan2.6-i2v":
        st.markdown("#### 🖼️ Image Input")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload local image (jpg, png, webp)",
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Upload an image to convert to video"
        )
        
        col_img1, col_img2 = st.columns([3, 1])
        
        with col_img1:
            # Show current image URL or placeholder
            if st.session_state.uploaded_image_url:
                default_url = st.session_state.uploaded_image_url
                st.success("✅ Image uploaded: %s" % default_url.split('/')[-1])
            else:
                default_url = ""
        
        # Handle file upload
        if uploaded_file is not None:
            # Read file data
            file_data = uploaded_file.getvalue()
            filename = uploaded_file.name
            
            # Show preview
            st.image(file_data, caption=filename, width=200)
            
            # Upload button
            if st.button("⬆️ Upload to Cloud", key="upload_btn"):
                with st.spinner("Uploading to catbox.moe..."):
                    # Try catbox first, then tmpfiles as fallback
                    image_url = upload_to_catbox(file_data, filename)
                    if not image_url:
                        image_url = upload_to_tmpfiles(file_data, filename)
                    
                    if image_url:
                        st.session_state.uploaded_image_url = image_url
                        st.success("✅ Uploaded: %s" % image_url)
                        st.rerun()
                    else:
                        st.error("❌ Upload failed")
        
        # Manual URL input (with pre-filled value if uploaded)
        img_url = st.text_input(
            "Image URL (for Image-to-Video)",
            value=st.session_state.uploaded_image_url or "",
            placeholder="https://example.com/image.jpg or uploaded URL",
            help="Required for image-to-video models. Leave empty if you just uploaded."
        )
        
        # Clear uploaded image
        if st.session_state.uploaded_image_url and img_url != st.session_state.uploaded_image_url:
            if st.button("🗑️ Clear Uploaded Image", key="clear_img"):
                st.session_state.uploaded_image_url = None
                st.rerun()

with col2:
    st.header("🚀 Actions")
    
    # Generate button
    generate_btn = st.button("🎬 Generate Video", type="primary", use_container_width=True)
    
    # Clear button
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.task_id = None
        st.session_state.task_status = None
        st.session_state.video_url = None
        st.session_state.progress = 0
        st.session_state.logs = []
        st.rerun()

# ============================================================
# HANDLE GENERATION
# ============================================================
if generate_btn:
    # Validate inputs
    if not st.session_state.api_url:
        st.error("❌ Please enter API URL in the sidebar")
    elif not st.session_state.api_key:
        st.error("❌ Please enter API Key in the sidebar")
    elif not prompt:
        st.error("❌ Please enter a prompt")
    else:
        # Auto-refine workflow
        final_prompt = prompt
        current_img_url = img_url if model == "video/wan2.6-i2v" and img_url else None
        
        if auto_refine:
            if not st.session_state.text_api_url or not st.session_state.text_api_key or not st.session_state.text_model:
                st.warning("⚠️ Auto-refine enabled but Text API not configured. Using original prompt.")
            else:
                with st.spinner("✨ Auto-optimizing prompt..."):
                    refined = refine_prompt(
                        st.session_state.text_api_url,
                        st.session_state.text_api_key,
                        st.session_state.text_model,
                        prompt,
                        current_img_url
                    )
                    if refined:
                        final_prompt = refined
                        st.session_state.refined_prompt = refined
                        st.success("✅ Prompt auto-optimized!")
                    else:
                        st.warning("⚠️ Refinement failed, using original prompt")
        
        # Build extra params
        extra_params = {
            "model": model,
            "seed": int(seed) if seed else None,
            "watermark": watermark,
            "prompt_extend": prompt_extend,
            "img_url": img_url if img_url else None
        }
        
        log_message("="*50)
        log_message("Starting video generation...")
        if auto_refine and final_prompt != prompt:
            log_message("Using refined prompt: %s" % final_prompt[:100])
        
        # Submit task
        result = submit_video_task(
            st.session_state.api_url,
            st.session_state.api_key,
            final_prompt,
            negative_prompt,
            resolution,
            duration,
            **extra_params
        )
        
        if "task_id" in result:
            st.session_state.task_id = result["task_id"]
            st.session_state.task_status = result.get("status", "QUEUED")
            
            # Show initial status
            st.info("📋 Task ID: %s" % result['task_id'])
            
            # Start polling
            with st.spinner("⏳ Polling for results..."):
                poll_result = poll_task_status(
                    st.session_state.api_url,
                    st.session_state.api_key,
                    st.session_state.task_id
                )
                
                if poll_result.get("videos"):
                    st.session_state.video_url = poll_result["videos"][0]["video_url"]
                    
        else:
            st.error("❌ Failed to submit task: %s" % result.get('error', 'Unknown error'))

# ============================================================
# STATUS DISPLAY
# ============================================================
st.markdown("---")
st.header("📊 Status")

if st.session_state.task_status:
    status = st.session_state.task_status
    progress = st.session_state.progress
    
    # Status display
    if status == "QUEUED":
        st.info("🔄 Queued - Waiting for processing")
    elif status == "PROCESSING":
        st.info("⚙️ Processing: %d%%" % progress)
        st.progress(progress / 100)
    elif status == "SUCCEED":
        st.success("✅ Video generation complete!")
    elif status == "FAILED":
        st.error("❌ Generation failed")
    else:
        st.write("Status: %s" % status)

# ============================================================
# VIDEO PLAYER
# ============================================================
if st.session_state.video_url:
    st.markdown("---")
    st.header("🎥 Result")
    
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    
    # Video player
    st.video(st.session_state.video_url)
    
    # Download button
    st.markdown("[📥 Download Video](%s)" % st.session_state.video_url)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.success("🎉 Video ready! Duration: %ds | Resolution: %s" % (duration, resolution))

# ============================================================
# LOGS
# ============================================================
if st.session_state.logs:
    st.markdown("---")
    with st.expander("📜 Logs", expanded=False):
        for log_entry in reversed(st.session_state.logs[-20:]):
            st.text(log_entry)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>OpenLens | Raw Transparency Pass-through | No Content Filtering</p>
    <p>Built with Streamlit</p>
    <hr style='margin: 10px 0; border-color: #333;'>
    <p style='color: #888; font-size: 11px;'>
        <strong>⚠️ Disclaimer:</strong> This tool serves as a transparent gateway only. 
        We do not store any API Keys or generated video content. 
        Please comply with relevant laws and regulations when using this service.
    </p>
</div>
""", unsafe_allow_html=True)
