import os

class NameRule:
    def apply(self, original_name):
        return original_name

class AddPrefixRule(NameRule):
    """规则 A: 加前缀"""
    def __init__(self, prefix):
        self.prefix = prefix

    def apply(self, original_name):
        # 修复：必须 return 修改后的字符串
        return f"{self.prefix}_{original_name}"

class ReplaceRule(NameRule):
    """规则 B: 替换文字"""
    def __init__(self, old_text, new_text):
        self.old_text = old_text
        self.new_text = new_text

    def apply(self, original_name):
        return original_name.replace(self.old_text, self.new_text)

class NumberingRule(NameRule):
    """规则 C: 序列化(001, 002...)"""
    def __init__(self, new_base_name):
        self.new_base_name = new_base_name
        self.counter = 1 # 记忆计数器

    def apply(self, original_name):
        # 自动获取原文件后缀名
        ext = os.path.splitext(original_name)[1]
        # zfill(3) 保证排序整齐 (001, 002...)
        new_name = f"{self.new_base_name}_{str(self.counter).zfill(3)}{ext}"
        self.counter += 1
        return new_name