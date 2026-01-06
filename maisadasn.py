import streamlit as st
import os
import random
import string
import requests

# ---------------------- 页面基础配置 ----------------------
st.set_page_config(
    page_title="朋友圈文案灵感库",
    page_icon="✨",
    layout="centered"
)

# 自定义样式
st.markdown("""
<style>
.stButton > button {border-radius: 8px; height: 40px; font-weight: 500;}
.stButton > button[data-testid="baseButton-primary"] {background-color: #8b5cf6; color: white;}
.stSelectbox > div > div, .stTextInput > div > div {border-radius: 8px; border: 1px solid #e5e7eb;}
.stSuccess, .stError, .stInfo {border-radius: 8px; padding: 16px; border: 1px solid #d1d5db;}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if "copied_text" not in st.session_state:
    st.session_state.copied_text = ""
if "btn_counter" not in st.session_state:
    st.session_state.btn_counter = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

# ---------------------- 工具函数 ----------------------
def generate_unique_key(prefix):
    st.session_state.btn_counter += 1
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{st.session_state.btn_counter}_{rand_str}"

def copy_to_clipboard(text):
    safe_text = text.replace("`", "\\`").replace("\n", "\\n").replace("'", "\\'")
    js_code = f"""
    <script>
    navigator.clipboard.writeText(`{safe_text}`)
    .then(() => {{alert('✅ 文案已复制！');}})
    .catch(() => {{alert('❌ 复制失败，请手动复制');}});
    </script>
    """
    st.write(js_code, unsafe_allow_html=True)

# ---------------------- Kimi API 调用（纯requests） ----------------------
def generate_friends_circle_copy(api_key, scene, style, custom_demand):
    try:
        url = "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": """你是朋友圈文案专家，生成3条50字内的文案，每条带1个emoji，序号标注，语言自然"""},
            {"role": "user", "content": f"场景：{scene}\n风格：{style}\n补充需求：{custom_demand}"}
        ]
        payload = {
            "model": "moonshot-v1-8k",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"], None
        else:
            return None, f"❌ 请求失败：{response.status_code}"
    except Exception as e:
        return None, f"❌ 生成失败：{str(e)}"

# ---------------------- 页面布局 ----------------------
st.title("✨ 朋友圈文案灵感库 AI助手")
st.divider()

with st.sidebar:
    st.subheader("⚙️ Kimi API配置")
    api_key = st.text_input("Kimi API密钥", type="password", placeholder="sk-xxxx")
    st.caption("密钥从https://platform.moonshot.cn获取")

st.subheader("📝 文案生成设置")
col1, col2 = st.columns(2)
with col1:
    scene = st.selectbox("场景", ["节日文案", "日常分享-美食", "日常分享-旅行"])
with col2:
    style = st.selectbox("风格", ["温馨治愈", "搞笑沙雕", "简约短句"])
custom_demand = st.text_input("补充需求", placeholder="比如：带蛋糕emoji")

st.divider()
generate_btn = st.button("🚀 生成文案", type="primary")

if generate_btn:
    if not api_key:
        st.error("⚠️ 请输入API密钥")
    else:
        with st.spinner("生成中..."):
            copy_result, error = generate_friends_circle_copy(api_key, scene, style, custom_demand)
            if copy_result:
                st.session_state.last_result = copy_result
                st.success(copy_result)
                st.button("📋 复制", on_click=copy_to_clipboard, args=(copy_result,))

if st.session_state.last_result:
    st.subheader("上次生成的文案")
    st.info(st.session_state.last_result)
