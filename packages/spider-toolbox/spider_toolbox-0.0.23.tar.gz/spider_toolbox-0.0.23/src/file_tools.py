import os
import shutil
from rich import print
import execjs


# 删除文件夹
def del_dir(dir_name: str, mode=1):
    """
    :param dir_name: 文件夹名字
    :param mode: 1为删除文件夹里面内容 2为连着文件夹一起删除
    :return:
    """
    if mode == 1:
        for file in os.listdir(dir_name):
            file_path = os.path.join(dir_name, file)
            os.remove(file_path)
    elif mode == 2:
        shutil.rmtree(dir_name)


# 格式化为可以创建的文件名
def format_str(data: str):
    # 去除字符串中的 ' / , \ , " , ? , * , < , > , | , : ,空格'
    return data.replace('/', '').replace('\\', '').replace('"', '').replace('?', '').replace('*', '') \
        .replace('<', '').replace('>', '').replace('|', '').replace(':', '').replace(' ', '')


# 创建文件夹
def mkdir(path, info=False):
    # 删除左右两边的空格 和 最后的 \
    path = path.strip().rstrip("\\")
    if os.path.exists(path):
        # print(' 创建过了')
        return False
    os.makedirs(path)
    if info:
        print(f'[yellow]{path} 创建成功[/]')
    return path


# 获取文件夹大小
def get_dir_size(dir):
    return sum(sum(os.path.getsize(os.path.join(root, name)) for name in files) for root, dirs, files in os.walk(dir))


# 获取硬盘信息
def get_ssd_info(path, show_mode='gb'):
    import shutil
    total, used, free = shutil.disk_usage(path)
    # bite/1024 kb/1024 mb/1024 gb
    if show_mode == 'gb' or show_mode == 'GB':
        size = 1024 ** 3
    elif show_mode == 'mb' or show_mode == 'MB':
        size = 1024 ** 2
    else:
        raise '输入正确字节单位'
    all_size = round(total / size, 2)
    used_size = round(used / size, 2)
    free_size = round(free / size, 2)
    return all_size, used_size, free_size


# 获取系统路径
def get_path(desktop=False, temp=False):
    if desktop:
        return os.path.join(os.path.expanduser("~"), 'Desktop')
    if temp:
        return os.getenv('TEMP')


# 打开js文件
def open_js(
        path_: str = '',
        encoding: str = 'utf-8',
        cwd: any = None
):
    '''
    :param path_: 文件路径
    :param encoding: 编码方式
    :param cwd: cwd
    :return: execjs.compile对象,可以直接.call调用
    '''
    path_ = path_.replace('\\', '/')
    if os.path.isfile(path_):
        with open(path_, 'r', encoding=encoding) as f:
            return execjs.compile(f.read(), cwd)
    else:
        raise '未找到该文件'
