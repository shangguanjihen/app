from Crypto.Cipher import AES
from multiprocessing import Pool  # 多进程爬取
from subprocess import Popen
import requests
import json
import re
import os
import threading
import shutil





# 分类信息头
headers = {
        'Authorization': 'Bearer',
        'version': '1.3.5',
        'Host': 'cnadmin.caomeisp666.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.12.0',
}


url4 = 'http://cnadmin.caomeisp666.com/api/videosort?uuid=37dadaea6ec29ab&device=0'
url6 = 'http://cnadmin.caomeisp666.com/api/videosort/{}?orderby=&page={}&uuid=37dadaea6ec29ab&device=0 '
url3 = 'https://honsuny.com/20200523/upiYLsKu/1000kb/hls/'
url2 = 'http://cnadmin.caomeisp666.com/api/videoplay/{}?uuid=37dadaea6ec29ab&device=0 '
path = os.path.dirname(os.path.abspath(__name__))

metux = threading.Lock()
# p = Popen("batch.bat", cwd=path)
# stdout, stderr = p.communicate()


# 运行bat文件,处理ts文件
def s_bat(title):
    print("开始处理ts文件")
    f = path + "\\" + "concat.bat"
    d = path + "\\" + title
    # 将bat文件放入视频文件中
    shutil.copy(f, d)
    # 运行视频文件目录中的bat文件，合成ts文件为MP4文件
    p = Popen("concat.bat", cwd=d)
    stdout, stderr = p.communicate()
    # 重命名
    c = d + "\\" + "new.MP4"
    e = d + "\\" + title + ".MP4"
    os.rename(c, e)
    # 转移文件到dowlod
    a = path + "\\" + "dowlod"
    shutil.move(e, a)
    # 删除文件夹
    os.rmdir(d)
    print("处理完成")

# 所有类别
def sort():
    html4 = requests.get(url4, headers=headers)
    # content4 = html4.content.decode('utf-8')
    content4 = html4.text
    # print(content4)
    con = json.loads(content4)['rescont']
    ids = []
    for x, y in enumerate(con):
        print(x+1, y['name'])
        ids.append((x, y['id']))
    return ids


# 单独类别
def d_sort(id, page=1):
    pool = Pool(4)  # 进程池对象
    for p in range(1, page+1):
        url = url6.format(id, p)
        html6 = requests.get(url)
        content = html6.content.decode('utf-8')
        con = json.loads(content)['rescont']['data']
        # print(con)
        print('正在下载第{}页视频：'.format(p))
        for t in con:
            print(t['title'])
        # 在dowlod.txt文件中记录已经下载的视频id
        for x in con:
            with open('dowlod.txt', 'r') as f:
                lis = f.readlines()
            for li in lis:
                if int(li) == x['id']:
                    print('已经下载', x['title'])
                    break
            else:
                with open('dowlod.txt', 'a+') as f:
                    f.write(str(x['id'])+'\n')
                pool.apply_async(info, args=(x['id'], ))
    # 这两句要放在循环之后，将所有进程运行完之后再关闭进程池，运行
    pool.close()
    pool.join()
    print("所选视频下载完毕")
    # print('一共下载了{}部视频'.format(page*15))
    # print(con)


# 获取播放信息
def info(id):
    url = url2.format(id)
    html2 = requests.get(url, headers=headers)
    content = html2.content.decode('utf-8')
    title = json.loads(content)['rescont']['title']
    title = re.sub(r'\?|\“|\”|\/|\\|\<|\>|\*||||\:| ', '', title)
    # 视频路径,获取到一个.m3u8文件，不过这不是最后的文件,
    # 在它的最后一行有个链接和scr拼接之后才是真正存放ts的.m3u8
    con = json.loads(content)['rescont']['videopath']
    scr = re.sub(r'index.*$', '1000kb/hls/', con)
    rcon = scr + 'index.m3u8'
    print('视频地址', rcon)
    # print(scr)
    # 获取.m3u8文件
    text = requests.get(rcon).content.decode('utf-8')
    # print(text)
    # 匹配出ts文件名
    ts = re.findall(r'(.+?\.ts)', text)
    # print(ts)
    # 获取加密值
    key = requests.get(scr+'key.key').content
    print(key)
    print('正在下载', title)
    a_path = path + '\\' + title
    d_path = path + '\\' + 'dowlod' + '\\' + title + '.MP4'
    # 如果文件夹和文件名不存在，就下载
    if not os.path.exists(a_path) and not os.path.exists(d_path):
        os.mkdir(a_path)
        # 多进程或线程，全局变量加锁
        # global sum
        # metux.acquire()
        # sum = sum+1
        # metux.release()
        for x, y in enumerate(ts):
            if y:
                s_url = scr + y
                # print(s_url)
                if x < 10:
                    b_path = a_path + '\\' + '0000' + str(x) + '.ts'
                elif x < 100:
                    b_path = a_path + '\\' + '000' + str(x) + '.ts'
                elif x < 1000:
                    b_path = a_path + '\\' + '00' + str(x) + '.ts'
                elif x < 10000:
                    b_path = a_path + '\\' + '0' + str(x) + '.ts'
                else:
                    b_path = a_path + '\\' + str(x) + '.ts'
                getVideoFile(b_path, s_url, key)
        # 每次下载后处理ts文件集
        s_bat(title)
    else:
        print('已经下载')


# 下载解密
def getVideoFile(b_path, url, key):
    """用于下载视频并完成解密
    :param b_path: 保存文件的目录
    :param url:下载的地址
    :param key:ts文件的key
    :param iv:ts文件加密的IV向量
    :return:    """
    print('准备从', url, '下载文件')
    # 下载注意开启流
    try:
        r = requests.get(url, timeout=(3, 10), stream=True).content
        # 开始构建解密方法
        mode = AES.MODE_CBC
        cryptor = AES.new(key, mode)
        if r:
            try:
                # 因为CBC加密解密的数据都要是16字节的倍数，所以在此检测ts文件是否是16字节的倍数。
                n = len(r) % 16
                r = r + b"0"*n
                # print(len(r))
                with open(b_path, 'wb') as f:
                    f.write(cryptor.decrypt(r))
                print('文件下载成功')
            except Exception as e:
                print('文件保存失败', e)
        else:
            print('文件下载失败')
    except Exception as e:
        print("下载失败，超时", e)


def main():
    while True:
        print('##########################################')
        ids = sort()
        global sum
        sum = 0
        n, page = input('请输入序号和页数，中间用空格分开.回车：').split(' ')
        n = int(n)
        if n in range(1, 100):
            id = ids[n - 1][1]
            # print(id)
            d_sort(id, int(page))
        else:
            print('请重新输入')


if __name__ == '__main__':
    main()

