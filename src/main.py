import os # 修复：必须导入 os 模块
from rules import AddPrefixRule, ReplaceRule, NumberingRule
from renamer import RenamerEngine

def main():
    print("=== 🚀 大厂标准批量改名工具 v3.0 ===")
    
    # 1. 场景设置
    folder = input("📂 请输入要处理的文件夹路径: ").strip()
    if not os.path.exists(folder):
        print("❌ 路径不存在！")
        return
        
    engine = RenamerEngine(folder)

    # 2. 策略选择
    print("\n请选择改名模式：")
    print("1. 添加前缀")
    print("2. 文字替换")
    print("3. 序列化重命名 (001, 002...)")
    choice = input("👉 请输入数字: ")

    rule = None
    if choice == "1":
        p = input("请输入前缀内容: ")
        rule = AddPrefixRule(p)
    elif choice == "2":
        old = input("要把什么字替换掉: ")
        new = input("替换成什么字: ")
        rule = ReplaceRule(old, new)
    elif choice == "3":
        base = input("请输入基础文件名: ")
        rule = NumberingRule(base)
    else:
        print("❌ 无效选择")
        return

    # 3. 预览预览 (Dry Run)
    print("\n--- 🔍 预览改名效果 ---")
    changes = engine.preview(rule)

    if not changes:
        print("⚠️ 没有文件需要修改。")
        return

    # 修复：必须使用 items() 而不是 item()
    for old, new in changes.items():
        print(f"📝 {old}  -->  {new}")

    # 4. 确认执行
    confirm = input(f"\n⚠️ 即将修改 {len(changes)} 个文件，确定吗？(y/n): ")
    
    if confirm.lower() == 'y':
        count = engine.execute(changes)
        print(f"\n🎉 搞定！共修改了 {count} 个文件。")
        
        # 5. 撤销功能
        undo_input = input("\n🤔 如果后悔了，可以输入 'u' 撤销操作，直接回车退出: ")
        if undo_input.lower() == 'u':
            u_count = engine.undo()
            print(f"⏪ 撤销成功！{u_count} 个文件已恢复原名。")
    else:
        print("\n🛡️ 操作已取消。")

if __name__ == "__main__":
    # 安全气囊：防止打包后的 exe 闪退
    try:
        main()
    except Exception as e:
        print(f"\n❌ 程序运行时发生致命错误: {e}")
    finally:
        input("\n按回车键退出程序...")