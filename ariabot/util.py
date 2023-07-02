import os

from urllib.parse import urlparse


def hum_convert(value):
    units = ["B/s", "KB/s", "MB/s", "GB/s", "TB/s", "PB/s"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value /= size


def byte2Readable(size):
    """
    递归实现，精确为最大单位值 + 小数点后三位
    """

    def strofsize(integer, remainder, level):
        if integer >= 1024:
            remainder = integer % 1024
            integer //= 1024
            level += 1
            return strofsize(integer, remainder, level)
        else:
            return integer, remainder, level

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    integer, remainder, level = strofsize(size, 0, 0)
    if level + 1 > len(units):
        level = -1
    return '{}.{:>03d}{}'.format(integer, remainder, units[level])


def progress(total_length, completed_length):
    if total_length != 0:
        return '{:.2f}%'.format(completed_length / total_length * 100)
    else:
        return "0%"


def getFileName(task):
    if task.__contains__('bittorrent'):
        if task['bittorrent'].__contains__('info'):
            # bt下载
            return task['bittorrent']['info']['name']
        # bt元信息
        return task['files'][0]['path']
    filename = task['files'][0]['path'].split('/')[-1]
    if filename == '':
        pa = urlparse(task['files'][0]['uris'][0]['uri'])
        filename = os.path.basename(pa.path)
    return filename


def split_list(datas, n, row: bool = True):
    """
    一维列表转二维列表，根据N不同，生成不同级别的列表
    """
    length = len(datas)
    size = length / n + 1 if length % n else length / n
    _datas = []
    if not row:
        size, n = n, size
    for i in range(int(size)):
        start = int(i * n)
        end = int((i + 1) * n)
        _datas.append(datas[start:end])
    return _datas
