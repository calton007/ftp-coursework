# ftp-coursework

Python3 + PySide6 FTP 图形客户端。

## 环境

- Python 3.11+
- FTP 服务器必须支持被动模式和 `MLSD`
- 不兼容 Python2/PyQt4

## 安装

```powershell
python -m pip install -r requirements.txt
```

## 启动

```powershell
python Login.py
```

## 功能

| 功能 | 说明 |
|---|---|
| 登录 | 支持用户名密码和匿名登录 |
| 浏览目录 | 使用 `MLSD` 严格识别文件/目录，展开目录时懒加载 |
| 上传文件 | 上传单个本地文件到选中的远程目录 |
| 下载文件 | 下载单个远程文件到本地目录 |
| 重命名 | 支持文件和文件夹重命名 |
| 新建文件夹 | 在选中的远程目录下创建文件夹 |
| 删除文件 | 删除前确认 |
| 递归删除文件夹 | 先枚举待删项，必须输入目录名确认；任一失败立即停止 |

## 测试

```powershell
pytest
```
