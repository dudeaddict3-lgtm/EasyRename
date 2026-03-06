import os

class RenamerEngine:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        # 只扫描文件，过滤掉文件夹
        self.files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        self.history = [] # 记录改名历史

    def preview(self, rule):
        """预览逻辑：返回 {旧名: 新名} 字典"""
        changes = {}
        for filename in self.files:
            new_name = rule.apply(filename)
            if new_name != filename:
                changes[filename] = new_name
        # 修复：必须返回字典，否则 main 会显示“无文件需要修改”
        return changes

    def execute(self, changes):
        """执行逻辑：真正写入硬盘"""
        success_count = 0
        self.history = [] # 每次执行前清空旧历史记录
        
        for old_name, new_name in changes.items():
            old_path = os.path.join(self.folder_path, old_name)
            new_path = os.path.join(self.folder_path, new_name)
            
            try:
                os.rename(old_path, new_path)
                # 记录 (新路径, 旧路径) 用于撤销
                self.history.append((new_path, old_path)) 
                print(f"✅ 成功: {old_name} -> {new_name}")
                success_count += 1
            except Exception as e:
                print(f"❌ 失败: {old_name} -> {e}")
        
        return success_count

    def undo(self):
        """撤销逻辑：反向执行历史记录"""
        if not self.history:
            print("⚠️ 没有可撤销的历史记录。")
            return 0

        undo_count = 0
        # 使用 reversed 确保从最后一个操作开始往回倒（后进先出）
        for new_path, old_path in reversed(self.history):
            try:
                os.rename(new_path, old_path)
                undo_count += 1
            except Exception as e:
                print(f"❌ 撤销失败: {e}")
        
        self.history = [] # 撤销完清空
        return undo_count