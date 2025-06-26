from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from Encase3D._cargo import *
from Encase3D._container import *

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['SimHei']


def draw_reslut(setted_container: Container):
    # 创建一个新的Figure对象
    fig: Figure = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    ax.view_init(elev=20, azim=40)
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

    # 计算 box_aspect 的比例
    aspect = (setted_container.length, setted_container.width, setted_container.height)
    max_dim = max(aspect)
    aspect = (aspect[0] / max_dim, aspect[1] / max_dim, aspect[2] / max_dim)
    ax.set_box_aspect(aspect)

    _draw_container(ax, setted_container)
    for cargo in setted_container._setted_cargos:
        _draw_cargo(ax, cargo)

    # 使用 block=True 确保图形窗口保持打开
    plt.show(block=True)


def _draw_container(ax, container: Container):
    # 绘制容器
    _plot_linear_cube(ax,
                      0, 0, 0,
                      container.length,
                      container.width,
                      container.height,
                      )

    # 绘制托盘，使用线条绘制出立体效果的木制托盘
    _plot_wooden_pallet(ax,
                        0, 0, -35,
                        container.length,
                        container.width,
                        35,  # 托盘的厚度
                        )


def _draw_cargo(ax, cargo: Cargo):
    _plot_opaque_cube(ax,
                      cargo.x, cargo.y, cargo.z,
                      cargo.length, cargo.width, cargo.height,
                      zorder=30
                      )


def _plot_opaque_cube(ax, x=10, y=20, z=30, dx=40, dy=50, dz=60,zorder=20):
    xx = np.linspace(x, x + dx, 2)
    yy = np.linspace(y, y + dy, 2)
    zz = np.linspace(z, z + dz, 2)
    xx2, yy2 = np.meshgrid(xx, yy)
    ax.plot_surface(xx2, yy2, np.full_like(xx2, z),zorder=zorder)
    ax.plot_surface(xx2, yy2, np.full_like(xx2, z + dz),zorder=zorder)
    yy2, zz2 = np.meshgrid(yy, zz)
    ax.plot_surface(np.full_like(yy2, x), yy2, zz2, zorder=zorder)
    ax.plot_surface(np.full_like(yy2, x + dx), yy2, zz2,zorder=zorder)
    xx2, zz2 = np.meshgrid(xx, zz)
    ax.plot_surface(xx2, np.full_like(yy2, y), zz2,zorder=zorder)
    ax.plot_surface(xx2, np.full_like(yy2, y + dy), zz2,zorder=zorder)


def _plot_linear_cube(ax, x, y, z, dx, dy, dz, color='red', zorder=10):
    xx = [x, x, x + dx, x + dx, x]
    yy = [y, y + dy, y + dy, y, y]
    kwargs = {'alpha': 1, 'color': color, 'zorder': zorder}
    ax.plot3D(xx, yy, [z] * 5, **kwargs)
    ax.plot3D(xx, yy, [z + dz] * 5, **kwargs)
    ax.plot3D([x, x], [y, y], [z, z + dz], **kwargs)
    ax.plot3D([x, x], [y + dy, y + dy], [z, z + dz], **kwargs)
    ax.plot3D([x + dx, x + dx], [y + dy, y + dy], [z, z + dz], **kwargs)
    ax.plot3D([x + dx, x + dx], [y, y], [z, z + dz], **kwargs)


def _plot_wooden_pallet(ax, x, y, z, length, width, thickness, color='brown', zorder=-10):
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
    ax.plot_surface(np.array([[x, x], [x, x]]), np.array([[y, y + width], [y, y + width]]), np.array([[z, z], [zz_top[0], zz_top[0]]]),
                    alpha=0.5, color=color, zorder=zorder)
    # 后侧面
    ax.plot_surface(np.array([[x + length, x + length], [x + length, x + length]]), np.array([[y, y + width], [y, y + width]]), np.array([[z, z], [zz_top[0], zz_top[0]]]),
                    alpha=0.5, color=color, zorder=zorder)
    # 左侧面
    ax.plot_surface(np.array([[x, x + length], [x, x + length]]), np.array([[y, y], [y, y]]), np.array([[z, z], [zz_top[0], zz_top[0]]]),
                    alpha=0.5, color=color, zorder=zorder)
    # 右侧面
    ax.plot_surface(np.array([[x, x + length], [x, x + length]]), np.array([[y + width, y + width], [y + width, y + width]]), np.array([[z, z], [zz_top[0], zz_top[0]]]),
                    alpha=0.5, color=color, zorder=zorder)

    # 绘制托盘的内部支撑线条并填充
    lines = np.arange(y, y + width, width / 7)
    lines = np.insert(lines, 0, y)  # 添加边缘线
    lines = np.append(lines, y + width)  # 添加边缘线

    # 填充边缘线与第一条线之间的区域
    ax.plot_surface(np.array([[x, x + length], [x, x + length]]), np.array([[lines[0], lines[0]], [lines[1], lines[1]]]), np.array([[zz_top[0], zz_top[0]], [zz_top[0], zz_top[0]]]),
                    alpha=0.5, color=color, zorder=zorder)

    for i in range(1, len(lines) - 1):
        if i % 2 == 1:
            # 填充当前线与前一条线之间的区域
            ax.plot_surface(np.array([[x, x + length], [x, x + length]]), np.array([[lines[i], lines[i]], [lines[i + 1], lines[i + 1]]]), np.array([[zz_top[0], zz_top[0]], [zz_top[0], zz_top[0]]]),
                            alpha=0.5, color=color, zorder=zorder)
        # 绘制当前线
        ax.plot3D([x, x + length], [lines[i], lines[i]], [zz_top[0], zz_top[0]], alpha=0.5, color=color, zorder=zorder)

    # 绘制边缘线
    ax.plot3D([x, x + length], [y, y], [zz_top[0], zz_top[0]], alpha=0.5, color=color, zorder=zorder)
    ax.plot3D([x, x + length], [y + width, y + width], [zz_top[0], zz_top[0]], alpha=0.5, color=color, zorder=zorder)

    # 绘制托盘的轮廓线
    ax.plot3D(xx, yy, zz, alpha=0.5, color=color, zorder=zorder)
    ax.plot3D(xx, yy, zz_top, alpha=0.5, color=color, zorder=zorder)
    for i in range(4):
        ax.plot3D([xx[i], xx[i]], [yy[i], yy[i]], [z, zz_top[0]], alpha=0.5, color=color, zorder=zorder)