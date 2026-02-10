# -*- coding: utf-8 -*-
"""
DeepSeek API 连接测试脚本
用于诊断 SSL、网络或配置问题
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from HOUDINI_HIP_MANAGER.utils.ai_client import OpenAIClient

def test_deepseek():
    print("=" * 60)
    print("DeepSeek API 连接测试")
    print("=" * 60)
    
    # 检查环境
    print("\n0. 环境检查...")
    import ssl
    print(f"   Python 版本: {sys.version}")
    print(f"   OpenSSL 版本: {ssl.OPENSSL_VERSION}")
    
    try:
        import requests
        print(f"   ✓ requests 库: {requests.__version__} (推荐)")
    except ImportError:
        print("   ✗ requests 库: 未安装（建议安装以获得更好的 SSL 兼容性）")
        print("   安装命令: pip install requests")
    
    client = OpenAIClient()
    
    # 检查 API Key
    print("\n1. 检查 API Key...")
    has_key = client.has_api_key('deepseek')
    if has_key:
        masked = client.get_masked_key('deepseek')
        print(f"   ✓ DeepSeek API Key 已配置: {masked}")
    else:
        print("   ✗ DeepSeek API Key 未配置")
        print("   请在环境变量中设置 DEEPSEEK_API_KEY 或在 config/houdini_ai.ini 中配置")
        return
    
    # 测试连接
    print("\n2. 测试 API 连接...")
    result = client.test_connection('deepseek')
    
    if result.get('ok'):
        print(f"   ✓ 连接成功!")
        print(f"   URL: {result.get('url')}")
        print(f"   状态: {result.get('status')}")
    else:
        print(f"   ✗ 连接失败!")
        print(f"   URL: {result.get('url')}")
        print(f"   错误: {result.get('error')}")
        print(f"   详情: {result.get('details', 'N/A')}")
    
    # 测试简单对话
    if result.get('ok'):
        print("\n3. 测试简单对话...")
        chat_result = client.chat(
            messages=[{'role': 'user', 'content': '你好，请用一句话介绍你自己。'}],
            model='deepseek-chat',
            provider='deepseek'
        )
        
        if chat_result.get('ok'):
            print(f"   ✓ 对话成功!")
            print(f"   回复: {chat_result.get('content')[:100]}...")
        else:
            print(f"   ✗ 对话失败!")
            print(f"   错误: {chat_result.get('error')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_deepseek()
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")
