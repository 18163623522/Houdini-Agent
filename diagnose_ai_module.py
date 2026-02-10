"""
Houdini AI 模块诊断脚本

用于检查当前加载的 AI 客户端模块是否正确。
如果遇到 API URL 格式错误（如 https://api.deepseek.comv1），
说明模块被缓存了，需要重新加载。
"""

def diagnose():
    print("=" * 60)
    print("Houdini AI 模块诊断")
    print("=" * 60)
    
    try:
        from HOUDINI_HIP_MANAGER.utils.ai_client import OpenAIClient
        
        print(f"\n✓ AI 客户端模块加载成功")
        print(f"  模块位置: {OpenAIClient.__module__}")
        
        # 检查 URL 配置
        openai_url = OpenAIClient.OPENAI_API_URL
        deepseek_url = OpenAIClient.DEEPSEEK_API_URL
        
        print(f"\n当前 API URL 配置：")
        print(f"  OpenAI  URL: {openai_url}")
        print(f"  DeepSeek URL: {deepseek_url}")
        
        # 验证 URL 格式
        issues = []
        
        if 'comv1' in openai_url or 'com//' in openai_url:
            issues.append("❌ OpenAI URL 格式错误（缺少斜杠）")
        else:
            print(f"\n  ✓ OpenAI URL 格式正确")
        
        if 'comv1' in deepseek_url or 'com//' in deepseek_url:
            issues.append("❌ DeepSeek URL 格式错误（缺少斜杠）")
        else:
            print(f"  ✓ DeepSeek URL 格式正确")
        
        if issues:
            print(f"\n" + "=" * 60)
            print("发现问题：")
            for issue in issues:
                print(f"  {issue}")
            print(f"\n解决方案：")
            print(f"  1. 关闭并重新打开 Houdini")
            print(f"  2. 或执行以下代码重新加载模块：")
            print(f"\n     import importlib")
            print(f"     from HOUDINI_HIP_MANAGER.utils import ai_client")
            print(f"     importlib.reload(ai_client)")
            print(f"     print('模块已重新加载')")
            print("=" * 60)
        else:
            print(f"\n" + "=" * 60)
            print("✓ 所有检查通过！模块配置正确。")
            print("=" * 60)
        
    except ImportError as e:
        print(f"\n❌ 无法导入 AI 客户端模块：{e}")
        print(f"\n   请确保在 Houdini 环境中运行此脚本。")
    except Exception as e:
        print(f"\n❌ 诊断过程出错：{e}")

def reload_module():
    """重新加载 AI 客户端模块"""
    print("=" * 60)
    print("重新加载 AI 客户端模块")
    print("=" * 60)
    
    try:
        import importlib
        from HOUDINI_HIP_MANAGER.utils import ai_client
        
        print("\n正在重新加载模块...")
        importlib.reload(ai_client)
        
        print("✓ 模块已重新加载")
        print("\n请重新运行诊断检查：")
        print("  diagnose()")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 重新加载失败：{e}")
        print("\n   建议关闭并重新打开 Houdini。")
        print("=" * 60)

if __name__ == "__main__":
    # 在 Houdini Python Shell 中运行
    diagnose()
    
    print("\n提示：如果发现问题，可以运行 reload_module() 尝试修复。")
