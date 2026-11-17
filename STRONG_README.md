# 大幅挥拍版本

导入 output_strong/All_3_Strong_HeadRelative.json。VaM 副本位于 Saves/PluginData/animations/HeadRelativeStrongSamples。父级固定为 Person#2/head，手腕轨道属于导入插件的人物，因此请在 Person#2 的 Timeline 中导入。

- 04_Strong_Sweep：2.1 秒，约 39 cm 蓄力位移，0.62 至 0.85 秒快速挥到参考点，再回收。
- 05_Strong_Diagonal：2.1 秒，更高的预备位置，斜向挥下。
- 06_Strong_Double：3.18 秒，两次完整蓄力挥拍。

新版启用手腕相对旋转，并增加 geometry 的 Right Fingers Fist、Right Fingers Grasp、Right Fingers In-Out、Right Thumb In-Out 四条轨道，设为 0 以回到自然张手基础姿势。这些名称已在本机场景数据中核对。若其他插件或单独手指 morph 仍控制手指，基础参数清零不保证完全伸直；需在实际场景检查。

手腕接触朝向使用头部局部欧拉角 (0,0,90) 的设计初值，并在蓄力和回弹时改变角度。此初值不是从当前人物实际姿势采样得到的，不能保证掌面已经准确朝向接触面。可以用以下参数重生成：

```bash
python generate_strong.py --atom 'Person#2' --palm-euler 0 0 90 --anchor 0.14 -0.03 0.08
```

旋转写为归一化四元数，位置和旋转时间完全对齐。大幅度和快速挥动表现用力感，但没有提高关节物理驱动力，也没有人为制作头部受击反应。手臂能否到达、碰撞和掌面朝向需要在 VaM 中验证；尚未运行预览。此版本仍然是自身头部旁的动作研究，不是改为拍打另一个人物。

右手位置和旋转控制应为 On。不要让旧版与新版同时驱动右手；导入后逐个选择新片段播放。手指 morph 会改变人物当前手型，停止动画不一定自动恢复原手型。
