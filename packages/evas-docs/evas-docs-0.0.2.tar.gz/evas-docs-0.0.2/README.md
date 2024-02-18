这个项目根据evas-docs更改而来，将依赖的pip包更新到了最新版本
支持Sphinx7.2.6，原来evas-docs只支持Sphinx4.5.0
主题由sphinx-idf-theme更换成了原版的sphinx-rtd-theme

参考项目链接：
evas-docs: https://github.com/espressif/esp-docs
sphinx-idf-theme: https://github.com/espressif/sphinx_idf_theme

# 环境准备 Windows和Linux都可以
Windows下生成pdf需要安装Latex和Perl环境，Latex建议Miktex，Miktex需要设置国内宏包源，并且设置根据需要自动下载宏包
Miktex: https://miktex.org/download
Perl: https://strawberryperl.com/

Windows需要下载GTK+ for Windows Runtime Environment 64-bit
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

记得一定要加上--no-dependencies参数不安装依赖，否则会额外安装一个xcffib包，导致生成报libxcb找不到的错误
pip install --no-dependencies -r requirements.txt

单独安装evas-docs，并将本项目src/evas-docs文件夹覆盖python安装目录下的Lib/site-packages/evas-docs
pip install --no-dependencies evas-docs

如果xcffib不小心被安装，可以使用如下命令卸载
pip uninstall xcffib -y

# 使用方法
切换到docs文件夹
cd docs

生成html
build-docs build 或 build-docs -l en

生成pdf
build-docs -bs latex -l en