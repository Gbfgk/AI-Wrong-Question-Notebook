"""
AI 错题本 - 构建脚本
使用 PyInstaller 打包为可执行文件
"""
import os
import sys
import subprocess
import shutil

def main():
    print("=" * 60)
    print("AI 错题本 - 构建可执行文件")
    print("=" * 60)
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")
    
    # 清理旧的构建文件
    if os.path.exists("build"):
        print("清理旧的 build 目录...")
        shutil.rmtree("build")
    
    if os.path.exists("dist"):
        print("清理旧的 dist 目录...")
        shutil.rmtree("dist")
    
    # 确保 templates 和 static 目录存在
    if not os.path.exists("templates"):
        print("错误：templates 目录不存在!")
        return
    
    if not os.path.exists("static"):
        print("错误：static 目录不存在!")
        return
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "AI_Wrong_Question_Notebook",
        "--onefile",
        "--windowed",  # 不显示控制台窗口（可选）
        "--add-data", f"templates{os.pathsep}templates",
        "--add-data", f"static{os.pathsep}static",
        "--hidden-import", "flask",
        "--hidden-import", "openai",
        "--hidden-import", "sqlite3",
        "--hidden-import", "hashlib",
        "app.py"
    ]
    
    print("\n开始打包...")
    print(f"命令：{' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 60)
        print("✓ 构建完成!")
        print(f"可执行文件位置：dist/AI_Wrong_Question_Notebook")
        print("\n首次运行时会自动提示配置 API 信息")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print(f"\n构建失败：{e}")
        return

if __name__ == "__main__":
    main()
