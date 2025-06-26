from typing import Iterable, List
from Encase3D._cargo import *
from Encase3D._container import *

class Strategy(object):
    # 继承此类 重写两个静态函数 实现自定义两个装载策略: 装箱顺序 和 货物.
    @staticmethod
    def encasement_sequence(cargos: Iterable, container: Container) -> Iterable:
        def sort_key(cargo):
            # 体积权重70%，长宽高匹配度权重30%
            vol_weight = cargo.volume * 0.7
            dim_weight = (
                                 min(container.length / cargo.length, 1.0) +
                                 min(container.width / cargo.width, 1.0) +
                                 min(container.height / cargo.height, 1.0)
                         ) * 0.3
            return -(vol_weight + dim_weight)  # 降序排列

        return sorted(cargos, key=sort_key)

    @staticmethod
    def choose_cargo_poses(cargo: Cargo, container: Container) -> list:
        # 根据容器剩余空间动态筛选姿态
        valid_poses = []
        for pose in CargoPose:
            l, w, h = cargo._shape_swiche[pose]
            # 假设当前放置点为 (0,0,0)，检查是否能放下
            if (l <= container.length and
                    w <= container.width and
                    h <= container.height):
                valid_poses.append(pose)
        # 按姿态生成的体积从大到小排序
        return sorted(valid_poses, key=lambda p: cargo._shape_swiche[p][0] *
                                                 cargo._shape_swiche[p][1] *
                                                 cargo._shape_swiche[p][2], reverse=True)

def encase_cargos_into_container(
    cargos:Iterable, 
    container:Container, 
    strategy:type
) -> float:
    sorted_cargos:List[Cargo] = strategy.encasement_sequence(cargos)
    i = 0 # 记录发当前货物
    while i < len(sorted_cargos):
        j = 0 # 记录当前摆放方式
        cargo = sorted_cargos[i]
        poses = strategy.choose_cargo_poses(cargo, container)
        while j < len(poses):
            cargo.pose = poses[j]
            is_encased = container._encase(cargo)
            if is_encased.is_valid:
                break # 可以装入 不在考虑后续摆放方式
            j += 1  # 不可装入 查看下一个摆放方式
        if is_encased.is_valid:
            i += 1 # 成功放入 继续装箱
        elif is_encased == Point(-1,-1,0):
            continue # 没放进去但是修改了参考面位置 重装
        else :
            i += 1 # 纯纯没放进去 跳过看下一个箱子
    return sum(list(map(
            lambda cargo:cargo.volume,container._setted_cargos
        ))) / container.volume



class VolumeGreedyStrategy(Strategy):
    @staticmethod
    def encasement_sequence(cargos:Iterable) -> Iterable:
        return sorted(cargos, key= lambda cargo:cargo.volume,reverse=1)

    @staticmethod
    def choose_cargo_poses(cargo:Cargo, container:Container) -> list:
        return list(CargoPose)