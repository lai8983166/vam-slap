# 播放时可调的拍打参考点

## 安装后的文件

- VaM/Custom/Scripts/SlapReference/SlapReferenceSetup.cs
- VaM/Saves/PluginData/animations/HeadRelativeAdjustable/All_3_Adjustable_Reference.json

## 操作顺序

1. 在 Person#2 的 Plugins 中新增一个插件，选择 SlapReferenceSetup.cs。保留原有 Timeline 插件。
2. 辅助插件自动创建 Empty Atom：SlapReference_Person2。状态 Ready 后再导入新版动画，避免父级不存在。
3. 在 Person#2 的 Timeline → More → Import / Export 中导入 All_3_Adjustable_Reference.json，选择名字带 _Adjustable 的片段播放。避免其他层同时驱动右手。
4. 在辅助插件点 Select reference handle，或在 VaM 选择 SlapReference_Person2。通过移动/旋转控制柄调整它。这个 Empty 是要拖动的对象，不是 rHandControl。
5. 参考点的位置和旋转状态保持 ParentLink，其目标是 Person#2/head。不要把它加入 Timeline 的动画轨道，否则拖动可能被动画覆盖。
6. 保存场景，保存参考点、父级连接、偏移和 Timeline 动画。仅导出 Timeline 动画不会带上 Empty Atom；换场景时需先创建参考点。

参考点位于原来的接触参考位置，初始相对头部位置 (0.14,-0.03,0.08)，旋转与头部一致。关键帧已减去此偏移，因此初始轨迹与旧版一致。参考点平移会移动整条轨迹，旋转会绕落点旋转整条轨迹及手腕朝向；头部移动旋转时整体跟随。

## 辅助插件按钮

- Create / reconnect reference：创建缺失的参考点，或重新连接头部；已有连接正常时保留用户偏移。
- Select reference handle：选中参考点控制器。
- Reset reference to default contact：明确重置位置和方向，会覆盖用户对参考点的调整。

插件不在 Update 中重写坐标，跟随和拖动偏移由 VaM 原生 ParentLink 处理。移除辅助插件不会删除 Empty；创建完成后原生连接仍由场景保存。固定 UID 已为当前 Person#2 场景配置，若同名对象已经存在则复用它，因此请不要给其他用途的对象使用 SlapReference_Person2 这个名字。

## 验证与边界

已用安装的 VaM 程序集编译检查辅助脚本（C# 6），并检查三段数据的位置重定位不改变初始轨迹、位置旋转帧时间一致。尚未在运行中的 VaM 场景验证 ParentLink 拖动、手臂可达性和碰撞效果。当前文件已经安装，但辅助插件尚未被加载到运行场景。

手掌方向与张手参数延用 strong 版本。可旋转参考点调节整体方向；如果仅想调整掌面而不转整条轨迹，需另外修改手腕旋转关键帧。参考点不会自动解决手臂够不到目标、手指仍被其他 morph 弯曲或物理碰撞的问题。
