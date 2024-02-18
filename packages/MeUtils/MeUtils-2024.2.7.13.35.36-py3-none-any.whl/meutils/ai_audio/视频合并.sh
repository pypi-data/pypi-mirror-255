#!/usr/bin/env bash
# @Project      : AI @by PyCharm
# @Time         : 2023/11/22 17:38
# @Author       : betterme
# @Email        : 313303303@qq.com
# @Software     : PyCharm
# @Description  :

ffmpeg -i /Users/betterme/Downloads/videoplayback.mp4 \
  -i audio_merged.wav \
  -vf "subtitles=new.srt" \
  -c:v libx264 -c:a aac \
  output.mp4


#在使用 `ffmpeg` 时，你可以通过 `-vf`（视频过滤器）选项调整字幕的位置。下面是一个例子，展示了如何使用 `subtitles` 过滤器来调整字幕的位置：
#
#```bash
#ffmpeg -i video.mp4 -vf "subtitles=subtitles.srt:force_style='MarginV=10,MarginL=20,MarginR=20'" -c:v libx264 -c:a copy output.mp4
#```
#
#在这个命令中：
#
#- `-vf "subtitles=subtitles.srt:force_style='MarginV=10,MarginL=20,MarginR=20'"`：这个过滤器指定了字幕文件，并通过 `force_style` 选项调整了字幕的样式。`MarginV` 是字幕距离视频底部的垂直边距，`MarginL` 是字幕距离视频左侧的水平边距，`MarginR` 是字幕距离视频右侧的水平边距。这些值都是以像素为单位的。
#
#请注意，`force_style` 选项允许你覆盖字幕文件中的样式。你可以设置字幕的字体、颜色、大小和位置等属性。在上面的例子中，我们只调整了字幕的边距，但你可以根据需要添加更多的样式属性。
#
#如果你的字幕是 ASS/SSA 格式，这些格式支持更丰富的样式选项，你可以直接在字幕文件中编辑这些样式，或者使用 `ffmpeg` 的 `force_style` 选项来覆盖它们。
#
#例如，如果你想要将字幕向上移动，你可以增加 `MarginV` 的值。如果你想要将字幕向左或向右移动，你可以调整 `MarginL` 和 `MarginR` 的值。
#
#请记住，调整字幕位置时，你可能需要根据视频的分辨率和字幕的原始位置进行实验，以找到最佳的显示效果。