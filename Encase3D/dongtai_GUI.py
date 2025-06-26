import pandas as pd
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import random
from matplotlib.colors import to_rgba
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QTextEdit)
from PyQt5.QtCore import Qt

# 配置参数
PALLET_THICKNESS = 30  # 托盘厚度
SPACING_x = 500  #
SPACING_y = 1500

class VisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.ani = None
        self.cargo_artists = []
        self.all_cargos = []
        self.selected_artist = None
        self.initUI()

    def initUI(self):
        # 主窗口设置
        self.setWindowTitle('托盘可视化系统')
        self.setGeometry(100, 100, 1200, 800)

        # 创建主部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # ===== 左侧控制面板 =====
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)
        control_layout.setSpacing(20)

        # 按钮样式
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 8px;
                min-width: 200px;
            }
            QPushButton:hover { background-color: #45a049; }
        """

        # 上传文件按钮
        self.upload_btn = QPushButton('上传托盘装载结果文件')
        self.upload_btn.setStyleSheet(button_style)
        self.upload_btn.clicked.connect(self.load_files)
        control_layout.addWidget(self.upload_btn)

        # 开始可视化按钮
        self.animate_btn = QPushButton('生成动态装载演示效果')
        self.animate_btn.setStyleSheet(button_style.replace('#4CAF50', '#008CBA'))
        self.animate_btn.clicked.connect(self.start_animation)
        control_layout.addWidget(self.animate_btn)

        # 新增静态可视化按钮
        self.static_btn = QPushButton('生成可视化结果')
        self.static_btn.setStyleSheet(button_style.replace('#4CAF50', '#9C27B0'))  # 紫色区分
        self.static_btn.clicked.connect(self.show_static_visualization)
        control_layout.addWidget(self.static_btn)

        # 状态标签
        self.status_label = QLabel('已选择0个文件')
        self.status_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.status_label)

        # 属性信息面板
        self.info_panel = QTextEdit()
        self.info_panel.setReadOnly(True)
        self.info_panel.setMinimumHeight(200)
        self.info_panel.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                line-height: 1.6;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 12px;
                background-color: #f8f9fa;
            }
        """)
        control_layout.addWidget(QLabel("<b>货物属性信息：</b>"))
        control_layout.addWidget(self.info_panel)

        # ===== 右侧可视化区域 =====
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(control_panel, stretch=2)
        layout.addWidget(self.canvas, stretch=5)

    def load_files(self):
        """加载托盘文件"""
        files, _ = QFileDialog.getOpenFileNames(self, '选择托盘数据文件', '', 'CSV文件 (*.csv)')
        if files:
            self.file_paths = files
            self.status_label.setText(f'已选择{len(files)}个文件')

    def start_animation(self):
        """启动可视化"""
        if not self.file_paths:
            self.status_label.setText('请先选择数据文件!')
            return

        # 重置状态
        self.selected_artist = None
        self.info_panel.clear()
        if self.ani:
            self.ani.event_source.stop()

        # 加载数据并初始化
        pallets = self.load_pallet_data(self.file_paths)
        self.figure.clf()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.view_init(elev=20, azim=40)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        # 创建动画
        total_frames = sum(len(p['cargos']) + 1 for p in pallets)
        self.cargo_artists = []
        self.all_cargos = []

        self.ani = FuncAnimation(
            self.figure,
            lambda i: self.animate(i, self.ax, pallets),
            frames=total_frames,
            interval=200,
            repeat=False,
            init_func=lambda: self.init_animation(pallets)
        )
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.draw()

    def init_animation(self, pallets):
        self.cargo_artists = []
        self.all_cargos = []
        return []

    def load_pallet_data(self, file_paths):
        """加载托盘数据（多行排列版本）"""
        pallets = []
        current_offset_x = 0
        current_offset_y = 0
        max_height_in_row = 0
        current_count_in_row = 0

        for idx, file_path in enumerate(file_paths):
            data = pd.read_csv(file_path)
            container = {
                'length': data.iloc[-1]['length'],
                'width': data.iloc[-1]['width'],
                'height': data.iloc[-1]['height']
            }

            # 换行逻辑
            if current_count_in_row >= 4:
                current_offset_x = 0
                current_offset_y += SPACING_y
                max_height_in_row = 0
                current_count_in_row = 0

            # 更新行高
            if container['height'] > max_height_in_row:
                max_height_in_row = container['height']

            # 处理货物数据
            cargos = [{
                'x': row['x'],
                'y': row['y'],
                'z': row['z'],
                'length': row['length'],
                'width': row['width'],
                'height': row['height']
            } for _, row in data[:-1].iterrows()]

            pallets.append({
                **container,
                'cargos': cargos,
                'colors': [to_rgba((random.random(), random.random(), random.random(), 0.5)) for _ in cargos],
                'offset_x': current_offset_x,
                'offset_y': current_offset_y
            })

            # 更新偏移量
            current_offset_x += container['length'] + SPACING_x
            current_count_in_row += 1

        return pallets

    def show_static_visualization(self):
        """直接显示完整可视化"""
        if not self.file_paths:
            self.status_label.setText('请先选择数据文件!')
            return

        # 重置状态
        self.selected_artist = None
        self.info_panel.clear()

        # 停止可能存在的动画
        if self.ani:
            self.ani.event_source.stop()

        # 加载数据
        pallets = self.load_pallet_data(self.file_paths)

        # 初始化画布
        self.figure.clf()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.view_init(elev=20, azim=40)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        # 设置坐标轴范围
        max_x = max(p['offset_x'] + p['length'] for p in pallets) if pallets else 0
        max_y = max(p['offset_y'] + p['width'] for p in pallets) if pallets else 0
        max_z = max(p['height'] for p in pallets) if pallets else 0
        self.ax.set_xlim(-SPACING_x, max_x + SPACING_x)
        self.ax.set_ylim(-SPACING_y, max_y + SPACING_y)
        self.ax.set_zlim(-PALLET_THICKNESS - 10, max_z + 50)

        # 绘制所有元素
        for p in pallets:
            self.draw_container(self.ax, p)
            self.draw_cargos(self.ax, p, len(p['cargos']))

        # 连接选择事件
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.draw()

    def animate(self, i, ax, pallets):
        """动画更新函数"""
        ax.cla()
        ax.view_init(elev=20, azim=40)

        # 设置坐标轴范围
        max_x = max(p['offset_x'] + p['length'] for p in pallets) if pallets else 0
        max_y = max(p['offset_y'] + p['width'] for p in pallets) if pallets else 0
        max_z = max(p['height'] for p in pallets) if pallets else 0
        ax.set_xlim(-SPACING_x, max_x + SPACING_x)
        ax.set_ylim(-SPACING_y, max_y + SPACING_y)
        ax.set_zlim(-PALLET_THICKNESS - 10, max_z + 50)

        # 绘制所有托盘
        for p in pallets:
            self.draw_container(ax, p)

        # 计算当前帧对应托盘
        current_total = 0
        for p_idx, pallet in enumerate(pallets):
            total_items = len(pallet['cargos']) + 1
            if current_total + total_items > i:
                local_i = i - current_total
                break
            current_total += total_items
        else:
            return

        # 绘制货物
        for prev_p in pallets[:p_idx]:
            self.draw_cargos(ax, prev_p, len(prev_p['cargos']))
        self.draw_cargos(ax, pallet, min(local_i, len(pallet['cargos'])))

    def draw_container(self, ax, pallet):
        """绘制托盘结构"""
        self._plot_wooden_pallet(
            ax,
            x=pallet['offset_x'],
            y=pallet['offset_y'],
            z=-PALLET_THICKNESS,
            length=pallet['length'],
            width=pallet['width'],
            thickness=PALLET_THICKNESS
        )

    def draw_cargos(self, ax, pallet, num_items):
        """绘制货物"""
        for i in range(num_items):
            cargo = pallet['cargos'][i]
            artist = self.draw_box(
                ax,
                x=cargo['x'] + pallet['offset_x'],
                y=cargo['y'] + pallet['offset_y'],
                z=cargo['z'],
                length=cargo['length'],
                width=cargo['width'],
                height=cargo['height'],
                color=pallet['colors'][i]
            )
            artist.set_picker(5)
            self.cargo_artists.append(artist)
            self.all_cargos.append({
                **cargo,
                'x': cargo['x'] + pallet['offset_x'],
                'y': cargo['y'] + pallet['offset_y'],
                'z': cargo['z']
            })

    def draw_box(self, ax, x, y, z, length, width, height, color):
        """绘制立方体"""
        vertices = [
            [x, y, z],
            [x + length, y, z],
            [x + length, y + width, z],
            [x, y + width, z],
            [x, y, z + height],
            [x + length, y, z + height],
            [x + length, y + width, z + height],
            [x, y + width, z + height]
        ]
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]],
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[2], vertices[3], vertices[7], vertices[6]],
            [vertices[0], vertices[3], vertices[7], vertices[4]],
            [vertices[1], vertices[2], vertices[6], vertices[5]]
        ]
        collection = Poly3DCollection(faces, facecolors=color,
                                      linewidths=1, edgecolors='r', alpha=0.5)
        ax.add_collection3d(collection)
        return collection

    def on_pick(self, event):
        """处理鼠标选择事件"""
        if event.artist not in self.cargo_artists:
            return

        # 清除之前的高亮
        if self.selected_artist:
            self.selected_artist.set_edgecolor('r')

        # 设置新的高亮
        index = self.cargo_artists.index(event.artist)
        cargo = self.all_cargos[index]
        event.artist.set_edgecolor('yellow')
        self.selected_artist = event.artist

        # 更新属性信息
        info = f"""
        <style>
            table {{ border-collapse: collapse; margin: 10px 0; }}
            td {{ padding: 5px 10px; border-bottom: 1px solid #ddd; }}
            .title {{ color: #2c3e50; font-weight: bold; }}
            .value {{ color: #3498db; }}
        </style>
        <div style='font-size: 14px'>
            <div class="title">货物属性：</div>
            <table>
                <tr><td>长度：</td><td class="value">{cargo['length']}mm</td></tr>
                <tr><td>宽度：</td><td class="value">{cargo['width']}mm</td></tr>
                <tr><td>高度：</td><td class="value">{cargo['height']}mm</td></tr>
                <tr><td colspan="2"><hr></td></tr>
                <tr><td>X坐标：</td><td class="value">{cargo['x']}mm</td></tr>
                <tr><td>Y坐标：</td><td class="value">{cargo['y']}mm</td></tr>
                <tr><td>Z坐标：</td><td class="value">{cargo['z']}mm</td></tr>
            </table>
        </div>
        """
        self.info_panel.setHtml(info)
        self.canvas.draw()

    def _plot_wooden_pallet(self, ax, x, y, z, length, width, thickness, color='brown', zorder=-10):
        # 绘制托盘的底面
        xx = [x, x, x + length, x + length, x]
        yy = [y, y + width, y + width, y, y]
        zz = [z, z, z, z, z]
        ax.plot3D(xx, yy, zz, color=color, zorder=zorder)

        # 绘制托盘的顶面
        zz_top = np.array(zz) + thickness  # 将列表转换为 NumPy 数组并加上厚度
        ax.plot3D(xx, yy, zz_top, color=color, zorder=zorder)

        # 填充托盘的侧面
        # 前侧面
        ax.plot_surface(np.array([[x, x], [x, x]]), np.array([[y, y + width], [y, y + width]]),
                        np.array([[z, z], [zz_top[0], zz_top[0]]]),
                        alpha=0.5, color=color, zorder=zorder)
        # 后侧面
        ax.plot_surface(np.array([[x + length, x + length], [x + length, x + length]]),
                        np.array([[y, y + width], [y, y + width]]), np.array([[z, z], [zz_top[0], zz_top[0]]]),
                        alpha=0.5, color=color, zorder=zorder)
        # 左侧面
        ax.plot_surface(np.array([[x, x + length], [x, x + length]]), np.array([[y, y], [y, y]]),
                        np.array([[z, z], [zz_top[0], zz_top[0]]]),
                        alpha=0.5, color=color, zorder=zorder)
        # 右侧面
        ax.plot_surface(np.array([[x, x + length], [x, x + length]]),
                        np.array([[y + width, y + width], [y + width, y + width]]),
                        np.array([[z, z], [zz_top[0], zz_top[0]]]),
                        alpha=0.5, color=color, zorder=zorder)

        # 绘制托盘的内部支撑线条并填充
        lines = np.arange(y, y + width, width / 7)
        lines = np.insert(lines, 0, y)  # 添加边缘线
        lines = np.append(lines, y + width)  # 添加边缘线

        # 填充边缘线与第一条线之间的区域
        ax.plot_surface(np.array([[x, x + length], [x, x + length]]),
                        np.array([[lines[0], lines[0]], [lines[1], lines[1]]]),
                        np.array([[zz_top[0], zz_top[0]], [zz_top[0], zz_top[0]]]),
                        alpha=0.5, color=color, zorder=zorder)

        for i in range(1, len(lines) - 1):
            if i % 2 == 1:
                # 填充当前线与前一条线之间的区域
                ax.plot_surface(np.array([[x, x + length], [x, x + length]]),
                                np.array([[lines[i], lines[i]], [lines[i + 1], lines[i + 1]]]),
                                np.array([[zz_top[0], zz_top[0]], [zz_top[0], zz_top[0]]]),
                                alpha=0.5, color=color, zorder=zorder)
            # 绘制当前线
            ax.plot3D([x, x + length], [lines[i], lines[i]], [zz_top[0], zz_top[0]], alpha=0.5, color=color,
                      zorder=zorder)

        # 绘制边缘线
        ax.plot3D([x, x + length], [y, y], [zz_top[0], zz_top[0]], alpha=0.5, color=color, zorder=zorder)
        ax.plot3D([x, x + length], [y + width, y + width], [zz_top[0], zz_top[0]], alpha=0.5, color=color,
                  zorder=zorder)

        # 绘制托盘的轮廓线
        ax.plot3D(xx, yy, zz, alpha=0.5, color=color, zorder=zorder)
        ax.plot3D(xx, yy, zz_top, alpha=0.5, color=color, zorder=zorder)
        for i in range(4):
            ax.plot3D([xx[i], xx[i]], [yy[i], yy[i]], [z, zz_top[0]], alpha=0.5, color=color, zorder=zorder)


if __name__ == '__main__':
    app = QApplication([])
    window = VisualizationApp()
    window.show()
    app.exec_()