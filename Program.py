from Encase3D import *
import random
import matplotlib.pyplot as plt

if __name__ == "__main__":
    plt.close('all')

    # 创建容器对象（长1200，宽1000，高2000）
    container = Container(1200, 1000, 2000)

    # 初始化货物列表
    cargos = []

    # 分层生成货物（总数量65个）
    # 小型货物：长(100-300) 宽(50-200) 高(50-200) - 45个
    for _ in range(45):
        l = random.randint(100, 300)
        w = random.randint(50, 200)
        h = random.randint(50, 200)
        cargos.append(Cargo(l, w, h))

    # 中型货物：长(300-500) 宽(200-400) 高(200-400) - 15个
    for _ in range(40):
        l = random.randint(300, 500)
        w = random.randint(200, 400)
        h = random.randint(200, 400)
        cargos.append(Cargo(l, w, h))

    # 大型货物：长(600-1000) 宽(500-800) 高(500-1000) - 5个
    for _ in range(20):
        l = random.randint(500, 800)
        w = random.randint(400, 700)
        h = random.randint(400, 800)
        cargos.append(Cargo(l, w, h))

    # 验证货物数量
    print(f"生成货物总数: {len(cargos)}个")

    # 执行装箱操作
    encasement_result = encase_cargos_into_container(
        cargos, container, VolumeGreedyStrategy
    )
    print(encasement_result)

    # 可视化保存结果（按需开启）
    #container.save_encasement_as_file()