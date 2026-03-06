import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

# 导入我们之前写的核心零件
# 注意：确保 gui_main.py 在项目根目录，这样才能找到 src 包
from src.rules import AddPrefixRule, ReplaceRule, NumberingRule
from src.renamer import RenamerEngine

class BatchRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("大厂批量改名神器 Pro (GUI版)")
        self.root.geometry("800x600")
        
        # 核心引擎 (先占位，等选了文件夹再初始化)
        self.engine = None
        self.current_folder = ""
        self.preview_changes = {}

        # === 1. 顶部：文件夹选择区 ===
        frame_top = ttk.LabelFrame(root, text="第一步：选择文件夹", padding=10)
        frame_top.pack(fill="x", padx=10, pady=5)

        self.lbl_path = ttk.Label(frame_top, text="未选择文件夹...")
        self.lbl_path.pack(side="left", fill="x", expand=True)
        
        btn_browse = ttk.Button(frame_top, text="📂 浏览...", command=self.select_folder)
        btn_browse.pack(side="right")

        # === 2. 中部：规则配置区 ===
        frame_mid = ttk.LabelFrame(root, text="第二步：配置规则", padding=10)
        frame_mid.pack(fill="x", padx=10, pady=5)

        # 模式选择下拉框
        ttk.Label(frame_mid, text="选择模式:").grid(row=0, column=0, padx=5, pady=5)
        self.mode_var = tk.StringVar(value="prefix")
        self.combo_mode = ttk.Combobox(frame_mid, textvariable=self.mode_var, state="readonly")
        self.combo_mode['values'] = ('添加前缀', '文字替换', '序列化重命名')
        self.combo_mode.current(0)
        self.combo_mode.grid(row=0, column=1, padx=5, pady=5)
        self.combo_mode.bind("<<ComboboxSelected>>", self.update_ui_inputs)

        # 动态输入框 (参数 1)
        self.lbl_param1 = ttk.Label(frame_mid, text="前缀内容:")
        self.lbl_param1.grid(row=1, column=0, padx=5, pady=5)
        self.entry_param1 = ttk.Entry(frame_mid, width=30)
        self.entry_param1.grid(row=1, column=1, padx=5, pady=5)

        # 动态输入框 (参数 2 - 仅替换模式用)
        self.lbl_param2 = ttk.Label(frame_mid, text="替换为:")
        self.entry_param2 = ttk.Entry(frame_mid, width=30)
        # 默认先隐藏第二行参数
        self.lbl_param2.grid_remove()
        self.entry_param2.grid_remove()

        # 预览按钮
        btn_preview = ttk.Button(frame_mid, text="🔍 生成预览 (Dry Run)", command=self.run_preview)
        btn_preview.grid(row=0, column=2, rowspan=2, padx=20, sticky="ns")

        # === 3. 底部：列表展示区 ===
        frame_list = ttk.LabelFrame(root, text="预览结果 (只会显示发生变化的文件)", padding=10)
        frame_list.pack(fill="both", expand=True, padx=10, pady=5)

        # 表格控件 (Treeview)
        columns = ("old_name", "new_name")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings")
        self.tree.heading("old_name", text="旧文件名")
        self.tree.heading("new_name", text="新文件名")
        self.tree.column("old_name", width=350)
        self.tree.column("new_name", width=350)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === 4. 底部按钮区 ===
        frame_action = ttk.Frame(root, padding=10)
        frame_action.pack(fill="x")

        self.btn_run = ttk.Button(frame_action, text="🚀 开始执行改名", command=self.run_execute, state="disabled")
        self.btn_run.pack(side="right", padx=5)

        self.btn_undo = ttk.Button(frame_action, text="⏪ 撤销上一步 (Undo)", command=self.run_undo, state="disabled")
        self.btn_undo.pack(side="right", padx=5)

    def select_folder(self):
        """选择文件夹逻辑"""
        path = filedialog.askdirectory()
        if path:
            self.current_folder = path
            self.lbl_path.config(text=path)
            # 初始化引擎
            self.engine = RenamerEngine(path)
            # 清空旧预览
            self.tree.delete(*self.tree.get_children())
            self.btn_run.config(state="disabled")
            messagebox.showinfo("就绪", f"已加载 {len(self.engine.files)} 个文件")

    def update_ui_inputs(self, event=None):
        """根据选择的模式，动态改变输入框的文字"""
        mode = self.combo_mode.get()
        if mode == '添加前缀':
            self.lbl_param1.config(text="前缀内容:")
            self.lbl_param2.grid_remove()
            self.entry_param2.grid_remove()
        elif mode == '文字替换':
            self.lbl_param1.config(text="要把什么字替换掉:")
            self.lbl_param2.grid(row=2, column=0, padx=5, pady=5) # 显示第二行
            self.entry_param2.grid(row=2, column=1, padx=5, pady=5)
            self.lbl_param2.config(text="替换成什么字:")
        elif mode == '序列化重命名':
            self.lbl_param1.config(text="基础文件名 (如 Photo):")
            self.lbl_param2.grid_remove()
            self.entry_param2.grid_remove()

    def run_preview(self):
        """核心逻辑：连接 Model 和 View"""
        if not self.engine:
            messagebox.showwarning("提示", "请先选择文件夹！")
            return

        # 1. 获取用户输入的参数
        p1 = self.entry_param1.get()
        p2 = self.entry_param2.get()
        mode = self.combo_mode.get()
        
        if not p1:
            messagebox.showwarning("提示", "输入框不能为空！")
            return

        # 2. 根据 GUI 选择，实例化对应的 Rule (多态的体现)
        rule = None
        if mode == '添加前缀':
            rule = AddPrefixRule(p1)
        elif mode == '文字替换':
            rule = ReplaceRule(p1, p2)
        elif mode == '序列化重命名':
            rule = NumberingRule(p1)

        # 3. 调用引擎生成预览
        self.preview_changes = self.engine.preview(rule)

        # 4. 更新表格界面
        self.tree.delete(*self.tree.get_children()) # 清空旧数据
        
        if not self.preview_changes:
            messagebox.showinfo("结果", "没有文件需要修改。")
            self.btn_run.config(state="disabled")
            return

        for old, new in self.preview_changes.items():
            self.tree.insert("", "end", values=(old, new))
        
        # 激活执行按钮
        self.btn_run.config(state="normal")

    def run_execute(self):
        """执行改名"""
        if not self.preview_changes:
            return
        
        if messagebox.askyesno("确认", f"即将修改 {len(self.preview_changes)} 个文件，确定吗？"):
            count = self.engine.execute(self.preview_changes)
            messagebox.showinfo("成功", f"成功修改了 {count} 个文件！")
            
            # 刷新界面
            self.tree.delete(*self.tree.get_children())
            self.btn_run.config(state="disabled")
            self.btn_undo.config(state="normal") # 激活撤销按钮
            
            # 重新扫描文件夹，更新文件列表
            # 这里简单处理，重新初始化引擎即可
            self.engine = RenamerEngine(self.current_folder)

    def run_undo(self):
        """执行撤销"""
        if messagebox.askyesno("撤销", "确定要撤销上一次操作吗？"):
            count = self.engine.undo()
            messagebox.showinfo("撤销成功", f"已恢复 {count} 个文件。")
            self.btn_undo.config(state="disabled")
            # 刷新引擎
            self.engine = RenamerEngine(self.current_folder)

if __name__ == "__main__":
    root = tk.Tk()
    # 设置一个稍微好看点的主题
    style = ttk.Style()
    style.theme_use('clam') 
    app = BatchRenamerGUI(root)
    root.mainloop()