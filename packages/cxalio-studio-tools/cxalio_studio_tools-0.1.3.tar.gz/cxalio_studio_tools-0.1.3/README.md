# cxalio-studio-tools

#### 介绍

这是一套用于简化影视后期工作的脚本合集。

涉及各种繁复的资料处理工作，解放双手，减少出错。

#### 安装

```shell
pip --install cxalio-media-tools

#推荐使用 pipx 安装
pipx --install cxalio-media-tools
```

#### 包含的工具

##### media-killer

media-killer 可以通过配置文件操纵 ffmpeg 批量地对大量媒体文件转码，
仅支持单文件输入，可以保留源文件的目录层级。
请查看[具体说明](media_killer/help.md)

##### subconv

subconv 是一个批量从字幕文件提取台词本的工具。
请查看[具体说明](src/subconv/help.md)

#### To-do

- media-inspector 解析媒体信息
