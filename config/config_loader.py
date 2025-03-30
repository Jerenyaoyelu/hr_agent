import yaml

def load_config(file_path="config/settings.yaml"):
    """
    加载 YAML 配置文件
    :param file_path: 配置文件路径，默认为 config/settings.yaml
    :return: 配置文件内容（字典）
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件未找到: {file_path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"解析 YAML 文件失败: {file_path}, 错误: {e}")