import os


def parse_auth_file(file_path):
    """
    解析用户名密码格式的文本文件
    :param file_path: 文本文件路径
    :return: 包含字典的列表，每个字典格式为 {'username': 'xxx', 'password': 'yyy'}
    """
    credentials = []

    file_path = os.path.expanduser(file_path)  # 解析 "~" 为用户目录

    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            # 跳过空行
            stripped_line = line.strip()
            if not stripped_line:
                continue

            # 检查分隔符是否存在
            if ':' not in stripped_line:
                print(f"警告：第 {line_num} 行缺少分隔符 ':' -> {line.strip()}")
                continue

            # 分割用户名和密码
            parts = stripped_line.split(':', 1)  # 只分割一次

            # 处理空用户名或密码的情况
            username = parts[0].strip()
            password = parts[1].strip() if len(parts) > 1 else ''

            if not username:
                print(f"警告：第 {line_num} 行用户名为空")
                continue

            credentials.append({
                'username': username,
                'password': password
            })

    return credentials


# 使用示例
if __name__ == "__main__":
    # 替换为你的文件路径
    file_path = '~/fourier-grx/resource/zenoh/credentials.txt'

    try:
        result = parse_auth_file(file_path)
        print(f"成功解析 {len(result)} 条凭证:")
        for cred in result:
            print(f"用户名: {cred['username']} \t 密码: {cred['password']}")
    except FileNotFoundError:
        print(f"错误：文件不存在 - {file_path}")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
