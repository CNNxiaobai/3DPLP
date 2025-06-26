# 3DPLP
# 1. Program.py（主程序入口）

核心作用：初始化容器和货物，执行装箱逻辑并输出结果。

关键功能：
创建 Container 容器对象（尺寸 1200x1000x2000。

随机生成 45 个小型、40 个中型、20 个大型货物（可以更换使用不同的数据集，这里只是为了进行实验）。

调用 encase_cargos_into_container 使用 VolumeGreedyStrategy 策略装箱（可以更换更复杂的策略）。

打印装箱结果（体积利用率）并提供可视化选项（注释中保留了保存结果的代码）。

# 2. Encase3D/__init__.py（策略定义与装箱入口）
核心作用：定义装箱策略接口和默认实现，提供装箱主函数。

关键代码：
Strategy 基类：声明 encasement_sequence（货物排序）和 choose_cargo_poses（摆放方式）两个抽象方法。

VolumeGreedyStrategy 类：继承 Strategy，按体积从大到小排序货物，固定使用所有摆放姿势。

encase_cargos_into_container 函数：遍历货物，尝试按策略摆放，返回体积利用率。

# 3. Encase3D/drawer.py（3D 可视化模块）
核心作用：绘制容器和货物的 3D 图形。

关键函数：
draw_reslut(setted_container)：主绘图入口，设置视角和比例，调用子函数绘制容器和货物。

_plot_opaque_cube：绘制不透明立方体（货物）。

_plot_linear_cube：绘制容器轮廓线。

_plot_wooden_pallet：绘制托盘，包含细节线条和填充效果。

# 4. Encase3D/_container.py（容器逻辑核心类）
核心作用：管理容器内的货物放置、碰撞检测、空间分配。

关键功能：
Container 类：
init：初始化容器尺寸和状态。

_encase(cargo)：尝试将货物放入容器，返回放置点或失败标志。

is_encasable(site, cargo)：检测货物是否可放置于指定位置。

_adjust_setting_cargo：调整货物位置以避免重叠。

save_encasement_as_file：保存装箱结果到 CSV 文件。

辅助函数 _is_rectangles_overlap 和 _is_cargos_collide：检测矩形或货物是否重叠。

# 5. Encase3D/_cargo.py（货物数据结构与操作）
核心作用：定义货物的姿态、属性和操作方法。

关键组件：

CargoPose 枚举：定义 6 种货物摆放姿势（如 tall_wide、short_thin 等）。

Point 类：表示三维坐标点，支持比较和有效性检查。

Cargo 类：
存储货物尺寸（通过姿态切换动态调整长宽高）。

提供体积计算、碰撞检测（通过投影矩形检测）。

属性访问器（如 x, y, z, length, width, height）。

# 6.Encase3D/dongtai_GUI.py（可视化结果展示后端）
核心作用：对装载结果进行可视化展示，可对任意符合数据规则的装载结果进行可视化展示。

Encase3D/jieguo文件夹中有很多已经生成好的csv结果文件，只要符合结果文件的格式都可以进行可视化展示。