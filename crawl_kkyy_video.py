import requests
import re
import urllib3
from urllib.parse import urljoin
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://103.51.147.112:51120"

def get_movie_list(channel_url):
    """从频道页获取所有电影详情页链接"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': BASE_URL + '/',
    }

    try:
        response = requests.get(channel_url, headers=headers, verify=False, timeout=10)
        response.encoding = 'utf-8'
        html = response.text

        # 提取所有 /detail/ 链接
        detail_links = re.findall(r'href="(/detail/\d+\.html)"', html)
        detail_links = list(set(detail_links))  # 去重

        return [urljoin(BASE_URL, link) for link in detail_links]
    except Exception as e:
        print(f"获取列表失败: {e}")
        return []

def get_play_links(detail_url):
    """从详情页获取所有播放链接"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': BASE_URL + '/',
    }

    try:
        response = requests.get(detail_url, headers=headers, verify=False, timeout=10)
        response.encoding = 'utf-8'
        html = response.text

        # 提取所有 /play/ 链接
        play_links = re.findall(r'href="(/play/\d+-\d+-\d+\.html)"', html)
        play_links = list(set(play_links))

        return [urljoin(BASE_URL, link) for link in play_links]
    except Exception as e:
        print(f"获取播放链接失败: {e}")
        return []

def extract_video_url(play_url):
    """从播放页提取视频地址"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': BASE_URL + '/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        response = requests.get(play_url, headers=headers, verify=False, timeout=10)
        response.encoding = 'utf-8'
        html = response.text

        # 多种模式匹配 m3u8 地址
        patterns = [
            r"'src':\s*\"([^\"]+\.m3u8)\"",
            r'"src":\s*"([^"]+\.m3u8)"',
            r'const\s+playSource\s*=\s*{[^}]+"src":\s*"([^"]+\.m3u8)"',
            r'https?://[^\s\'"]+\.m3u8[^\s\'"]*',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.I)
            if matches:
                video_url = matches[0]
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                return video_url

        return None
    except Exception as e:
        print(f"提取视频失败: {e}")
        return None

def crawl_movies(channel_url, max_movies=5):
    """爬取电影列表及视频地址"""
    print(f"正在爬取频道: {channel_url}")

    # 1. 获取所有电影详情页
    detail_urls = get_movie_list(channel_url)
    print(f"找到 {len(detail_urls)} 部电影")

    results = []
    for i, detail_url in enumerate(detail_urls[:max_movies]):
        print(f"\n处理第 {i+1} 部电影: {detail_url}")

        # 2. 从详情页获取播放链接
        play_urls = get_play_links(detail_url)
        if not play_urls:
            print("  没有找到播放链接")
            continue

        # 3. 从第一个播放链接提取视频地址
        play_url = play_urls[0]
        print(f"  播放页: {play_url}")
        video_url = extract_video_url(play_url)

        if video_url:
            print(f"  ✅ 视频地址: {video_url}")
            results.append({
                'detail_url': detail_url,
                'play_url': play_url,
                'video_url': video_url
            })
        else:
            print("  ❌ 未找到视频地址")

    return results

if __name__ == "__main__":
    # 爬取电影频道
    results = crawl_movies(
        channel_url=BASE_URL + "/channel/1.html",
        max_movies=3
    )

    print("\n" + "=" * 60)
    print("爬取结果汇总:")
    for r in results:
        print(f"  电影: {r['detail_url']}")
        print(f"  视频: {r['video_url'][:80]}...")
    print("=" * 60)