# 本文档在于指导用户自行编译打包源码

## 框架选取———Kivy

---

Kivy 是一个开源的跨平台Python 框架，用于开发使用创新的多点触控用户界面的应用程序。目的是允许快速轻松的交互设计和快速原型制作，同时使代码可部署。

## 源码依赖项

---

```
pip install kivy=2.1.0
pip install kivymd
```

同时我们还使用了由百度开源的深度学习模型——PaddlePaddle来实现我们的药品包装盒的识别，关于OCR引擎的下载，参考一下：

- 如果您的机器上安装了 CUDA 9 或 CUDA 10，请运行以下命令进行安装

```
python -m pip install paddlepaddle-gpu -i https://pypi.tuna.tsinghua.edu.cn/simple
```

- 如果您的机器上没有可用的 GPU，请运行以下命令安装 CPU 版本

```
python -m pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
```

- 安装PaddleOCR Whl包

```
pip install "paddleocr>=2.0.1" # Recommend to use version 2.0.1+
```

此外我们还使用了一款功能强大的开源搜索引擎——MeiliSearch
下载本地服务器只需下载文件链接中提供的**eilisearch-windows-amd64.exe**

## 运行主程序

---

当已经下载好了所有依赖项时，您可以在您的**python IDE**或者在终端运行:

```
--cd KivyApp
--python main.py
```

即可在本地编译运行app程序

## 重新打包为apk

---

- 安装构建器

```
# via pip (latest stable, recommended)
# if you use a virtualenv, don't use the `--user` option
pip install --user buildozer

# latest dev version
# if you use a virtualenv, don't use the `--user` option
pip install --user https://github.com/kivy/buildozer/archive/master.zip

# git clone, for working on buildozer
git clone https://github.com/kivy/buildozer
cd buildozer
python setup.py build
pip install -e .
```

- 检查 buildozer 在你的路径中

```
`which buildozer`
# if there is no result, and you installed with --user, add this line at the end of your `~/.bashrc` file.
export PATH=~/.local/bin/:$PATH
# and then run
. ~/.bashrc
```

- 进入您的应用程序目录并运行：

```
buildozer init
# edit the buildozer.spec, then
buildozer android debug deploy run
```

运行paddlehub云服务的指令：

hub serving start -m chinese_ocr_db_crnn_server
