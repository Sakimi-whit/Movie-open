import requests
from bs4 import BeautifulSoup
import re
import json

# 目标页面 URL
url = 'https://103.51.147.112:51120/channel/1.html'

# 忽略 SSL 证书验证（因为 IP 地址的自签名证书）
session = requests.Session()
session.verify = False

# 设置请求头（模拟浏览器）
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://103.51.147.112:51120/',
}

def get_video_url(page_url):
    print(f"正在访问: {page_url}")
    response = session.get(page_url, headers=headers, timeout=10)
    response.encoding = 'utf-8'  # 有时需要调整编码
    html = response.text

    # ---- 方法1：直接查找 <video> 或 <source> 标签 ----
    soup = BeautifulSoup(html, 'html.parser')
    video_tag = soup.find('video')
    if video_tag and video_tag.get('src'):
        video_url = video_tag['src']
        # 处理相对路径
        if video_url.startswith('//'):
            video_url = 'https:' + video_url
        elif video_url.startswith('/'):
            video_url = 'https://103.51.147.112:51120' + video_url
        return video_url

    source_tag = soup.find('source')
    if source_tag and source_tag.get('src'):
        video_url = source_tag['src']
        # 处理相对路径
        if video_url.startswith('//'):
            video_url = 'https:' + video_url
        elif video_url.startswith('/'):
            video_url = 'https://103.51.147.112:51120' + video_url
        return video_url

    # ---- 方法2：查找 iframe，可能嵌套播放器 ----
    iframe = soup.find('iframe')
    if iframe and iframe.get('src'):
        iframe_src = iframe['src']
        if not iframe_src.startswith('http'):
            iframe_src = 'https://103.51.147.112:51120' + iframe_src
        print(f"发现 iframe，尝试递归获取: {iframe_src}")
        # 递归调用自身获取 iframe 内的视频
        return get_video_url(iframe_src)

    # ---- 方法3：查找 JSON 数据（常见于 XHR 加载） ----
    # 尝试在页面中查找类似 "video_url":"..." 的字符串
    match = re.search(r'"video_url"\s*:\s*"([^"]+)"', html)
    if match:
        return match.group(1)
    # 尝试查找 m3u8 或 mp4 链接
    match = re.search(r'(https?://[^\s\'"]+\.(m3u8|mp4)[^\s\'"]*)', html)
    if match:
        return match.group(1)

    # ---- 方法4：分析 XHR 请求（需要抓包）----
    # 这里你可以根据之前 Network 面板看到的 API 地址添加
    # 例如：api_url = 'https://103.51.147.112:51120/api/video?id=1'
    # 然后发送请求获取 JSON

    print("未找到视频链接，请检查页面结构。")
    return None

# 执行
video_url = get_video_url(url)
if video_url:
    print(f"✅ 获取到视频链接: {video_url}")
else:
    print("❌ 未能提取视频链接，需要进一步分析。")