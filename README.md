# Timeline 头部相对拍打样例

基于本机 AcidBubbles.Timeline.287.var 中的 ImportExportScreen、AtomAnimationSerializer、CurveTypeValues 生成。导入格式版本为 283；这不是插件版本写错。

## 文件与导入

- output/All_3_HeadRelative_Taps.json：包含全部三个片段。
- output/01_Soft_Tap.json：1.8 秒，轻拍后收手。
- output/02_Wide_Sweep.json：2.1 秒，加大预备幅度、快速挥拍、缓慢收手。
- output/03_Double_Tap.json：2 秒，两次拍打后收手。

在人物加载 Timeline 287，进入 More → Import / Export → Import animation，选择合集或单个文件，在导入分配页面确认，随后在动画列表逐个选择并播放。合集与单文件二选一，避免重复导入。片段不循环、不自动播放。

当前样例父级 Atom UID 为 Person，刚体为 head；尚待替换为实际场景 UID。生成器现在要求显式提供 --atom，不再默认猜测人物名称。Parent.Atom 不会自动指向导入人物。右手轨道未指定 Atom，故它属于导入人物。

```bash
python generate.py --atom 'Person#2'
```

人物的右手控制器位置需要处于 On；同一右手不要同时被其他动画层或插件驱动。三个片段应作为同层的不同动画播放，而非同时叠加。

## 坐标与限制

全部位置单位为米，时间为秒，XYZ 是 head 刚体的局部轴，不是房间坐标。默认参考点为 (0.14, -0.03, 0.08)，是待校准的头侧样例点，不是经过模型验证的皮肤接触点。轨迹沿局部 +X 一侧收放；这不保证对应模型解剖学上的右侧。根据模型实际效果调整方向与位置。

这版只驱动 rHandControl 的位置，不驱动头、躯干、肘、手指，也不驱动手掌旋转。因此它是可供预览、调节的拍打轨迹样例，不是已验证的完整接触动画。先把手掌和手指摆成需要的姿势。手掌朝向不会因本文件自动跟随头部旋转；如需完整掌面跟随，需要采样实际手部相对头部四元数并启用 Rotation。

修改参考点和挥动幅度：

```bash
python generate.py --atom Person --anchor 0.14 -0.03 0.08 --scale 0.7
```

scale 只缩放相对参考点的挥动幅度，不改变参考点。要换到相反方向，可以编辑 generate.py 中 DESIGNS 的局部位移。只改 Parent.Atom 字符串保持数值不变，可保持这些数值相对于另一个头部的语义；通过界面重新 Parenting 则可能触发 Timeline 的轨道自动偏移，结果不同。

## 数据结构

顶层包含 SerializeVersion、AtomType 和 Clips；每个片段包含 Controllers。每个控制器的 X/Y/Z/RotX/RotY/RotZ/RotW 都是一组 {t,v,c} 关键帧。t 是秒，v 是数值，c=1 是 Flat，c=2 是 Linear。旋转采用四元数而非欧拉角。

TargetsRotation=1 保留完整控制器轨道，使本版本界面显示 Parenting；ControlRotation=0 禁用旋转实际驱动。Rot 数组中的单位四元数是占位值，不能直接开启 Rotation 并把它当成校准后的掌面朝向。

示例：轻拍的关键时刻为 0 秒准备、0.35 秒预备、0.73 秒到达参考点、0.88 秒回弹、1.45 秒回到准备位置、1.8 秒结束。三条位置曲线的首尾一致，方便重复预览。

已检查 JSON 可解析、各曲线时间递增、首末关键帧覆盖片段长度，以及位置和旋转的全部关键帧时间完全一致，字段对照本机源码。首版的旋转帧数不匹配问题已修复。当前场景报告 Person 父级不存在，必须替换实际 UID 后再导入。尚未在 VaM 中实际导入和播放验证；接触、手臂可达性以及物理反馈需要场景验证。
