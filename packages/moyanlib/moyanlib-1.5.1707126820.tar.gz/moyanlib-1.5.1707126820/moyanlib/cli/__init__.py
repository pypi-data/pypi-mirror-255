import click
import moyanlib
import platform as pf
import time as _time
import hashlib as h
import os


@click.group()
def cli():
    pass


@cli.command(help="清除pyc")
def clear_pyc():
    # 使用os遍历所有目录
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.split(".")[-1] == "pyc":
                path = os.path.join(root, file)
                print("正在删除：" + path)
                os.remove(path)
    click.echo("清除完成")


@cli.command(help="生成设备ID")
def DeviceId():
    click.echo(moyanlib.getDeviceID())


@cli.group(help="获取当前时间")
def time():
    click.echo(_time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime()))


@time.command(help="获取当前时间戳")
@click.option("--three", help="13位时间戳", is_flag=True, default=False)
def get_timestamp(three):
    if three:
        click.echo(_time.time())
    else:
        click.echo(int(_time.time()))


@time.command(help="获取当前时间（可自定义）")
@click.option("--format", "-f", help="时间格式", default="%Y-%m-%d %H:%M:%S")
def get_time(formats):
    click.echo(_time.strftime(formats, _time.localtime()))


@cli.group(help="文件操作")
def file():
    pass


@file.command(help="创建文件夹")
@click.argument("path")
def mkdir(path):
    if os.path.exists(path):
        click.echo("文件夹已存在")
    else:
        os.mkdir(path)
        click.echo("文件夹创建成功")
