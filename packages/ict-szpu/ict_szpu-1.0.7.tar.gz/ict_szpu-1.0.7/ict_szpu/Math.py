import math

def drawRound(centerPoint:[float,float,float],radius:float,numPoints:int):
    """
    计算圆形的轨迹(单无人机)
    :param centerPoint:圆心坐标点
    :param radius:半径
    :param numPoints:生成点的数量
    :return:返回list[float,float,float]
    """
    points=[]
    for i in  range(numPoints):
        angleInRadians=math.pi*2/numPoints*i
        x=radius*math.sin(angleInRadians)
        y=radius*math.cos(angleInRadians)
        points.append([x+centerPoint[0],y+centerPoint[1],0+centerPoint[2]])

    return  points


def drawElliptic(center:[float,float,float],radiusX:float,radiusY:float,detalangle:float):
    """
    计算椭圆的轨迹(单无人机)
    :param center: 中心点
    :param radiusX: x半径
    :param radiusY: y半径
    :param detalangle: 间隔角度
    :return:返回list[float,float,float]
    """
    points=[]
    angle=0
    while angle<=math.pi*2:
        x=center[0]+radiusX*math.sin(angle)
        y=center[1]-radiusY*math.cos(angle)
        points.append([x,y,center[2]])
        angle+=detalangle

    return  points


def drawSin(center:[float,float,float],A:float,pointNum:float,cycle:int):
    """
    计算sin轨迹(单无人机)
    :param center: 起点原点
    :param A: y轴系数
    :param pointNum: 一个周期内点的数量（不得小于5，点越多，形状越像）
    :param cycle: 周期数
    :return:返回list[float,float,float]
    """
    points=[]
    if pointNum<=5:
        print("一个周期点数不得小于5")
        return points

    x=0
    detal=2*math.pi/pointNum
    while x<=math.pi*2*cycle:
        y=math.sin(x)*A
        points.append([x+center[0], y+center[1], center[2]])
        x+=detal

    return  points

def drawCube(centerPoint:[float,float,float],length:float,wighth:float,high:float):
    """
    计算立方体轨迹(单无人机)
    :param centerPoint:立方体中心点
    :param length:长
    :param wighth:宽
    :param high:高
    :return:
    """
    points = [[0,0,0],
              [length,0,0],
              [length,high,0],
              [0,high,0],
              [0,0,0],
              [0,0,wighth],
              [length,0,wighth],
              [length,0,0],
              [length,high,0],
              [length,high,wighth],
              [length,0,wighth],
              [length,high,wighth],
              [0,high,wighth],
              [0,0,wighth],
              [0,high,wighth],
              [0,high,0]]

    # 中心点偏移矫正
    for i in points:
        i[0]+=(centerPoint[0]-length/2)
        i[1]+=(centerPoint[1]-high/2)
        i[2]+=(centerPoint[2]-wighth/2)

    return points

def drawSphere(centerPoint:[float,float,float],radius:float,numPoints:int):
    """
    计算球体轨迹(单无人机)
    :param centerPoint: 中心点
    :param radius: 半径
    :param numPoints: 一个圆的数量（建议设置为4的倍数）
    :return:
    """
    point2ds = []
    point3ds = []
    for i in range(numPoints+1):
        angleInRadians = math.pi * 2 / numPoints * i
        x = radius * math.sin(angleInRadians)
        y = radius * math.cos(angleInRadians)
        point2ds.append([x,y])

    # 第一个圆
    for p2d in point2ds:
        point3ds.append([p2d[0],p2d[1],0])
    # 第二个圆
    for p2d in point2ds:
        point3ds.append([0,p2d[1],p2d[0]])

    #1/4半圆
    for i in range(numPoints+1):
        angleInRadians = math.pi / 2 / numPoints * i
        x = radius * math.sin(angleInRadians)
        y = radius * math.cos(angleInRadians)
        point3ds.append([0,y,x])

    # 第三个圆
    for p2d in point2ds:
        point3ds.append([p2d[0],0,p2d[1]])

    # 中心点偏移矫正
    for i in point3ds:
        i[0]+=centerPoint[0]
        i[1]+=centerPoint[1]
        i[2]+=centerPoint[2]

    return point3ds

def drawCylinder(centerPoint:[float,float,float],radius:float,high:float,numPoints:int):
    """
    计算球体轨迹(单无人机)
    :param centerPoint: 中心点
    :param radius: 半径
    :param high: 高度
    :param numPoints: 一个圆的数量（建议设置为4的倍数）
    :return:
    """
    point2ds = []
    point3ds = []
    for i in range(numPoints+1):
        angleInRadians = math.pi * 2 / numPoints * i
        x = radius * math.sin(angleInRadians)
        y = radius * math.cos(angleInRadians)
        point2ds.append([x,y])

    # 第一个圆
    for p2d in point2ds:
        point3ds.append([p2d[0],0,p2d[1]])

    # 第二个圆
    for p2d in point2ds:
        point3ds.append([p2d[0],high,p2d[1]])

    # 1/4圆
    for i in range(numPoints+1):
        angleInRadians = math.pi / 2 / numPoints * i
        x = radius * math.sin(angleInRadians)
        y = radius * math.cos(angleInRadians)
        point3ds.append([x,high,y])

    # 下去
    point3ds.append([point3ds[-1][0],0,point3ds[-1][2]])

    # 2/4圆
    for i in range(numPoints+1):
        angleInRadians = math.pi / 2 / numPoints * i + math.pi / 2
        x = radius * math.sin(angleInRadians)
        y = radius * math.cos(angleInRadians)
        point3ds.append([x,0,y])

    # 上去
    point3ds.append([point3ds[-1][0], high, point3ds[-1][2]])

    # 3/4圆
    for i in range(numPoints+1):
        angleInRadians = math.pi / 2 / numPoints * i + math.pi
        x = radius * math.sin(angleInRadians)
        y = radius * math.cos(angleInRadians)
        point3ds.append([x,high,y])

    # 下去
    point3ds.append([point3ds[-1][0],0,point3ds[-1][2]])

    # 中心点偏移矫正
    for i in point3ds:
        i[0]+=(centerPoint[0])
        i[1]+=(centerPoint[1]-high/2)
        i[2]+=(centerPoint[2])

    return point3ds

def drawCone(centerPoint:[float,float,float],radius:float,high:float,numPoints:int):
    """
    计算球体轨迹(单无人机)
    :param centerPoint: 中心点
    :param radius: 半径
    :param high: 高度
    :param numPoints: 一个圆的数量（建议设置为4的倍数）
    :return:
    """
    point2ds = []
    point3ds = []
    for i in range(numPoints+1):
        angleInRadians = math.pi * 2 / numPoints * i
        x = radius * math.sin(angleInRadians)
        y = radius * math.cos(angleInRadians)
        point2ds.append([x,y])

    # 第一个圆
    for p2d in point2ds:
        point3ds.append([p2d[0],0,p2d[1]])

    # 顶点
    point3ds.append([0, high,0])

    # 退到1/4
    point3ds.append([radius,0,0])

    # 顶点
    point3ds.append([0, high,0])

    # 退到2/4
    point3ds.append([0,0,-radius])

    # 顶点
    point3ds.append([0, high,0])

    # 退到3/4
    point3ds.append([-radius,0,0])

    # 中心点偏移矫正
    for i in point3ds:
        i[0]+=(centerPoint[0])
        i[1]+=(centerPoint[1])
        i[2]+=(centerPoint[2])

    return point3ds

def drawSphere_complex(center:[float,float,float],radius :float,num_Sqr :int):
    """
    计算球面点集(多无人机)
    :param center: 中点坐标
    :param radius: 半径
    :param num_Sqr: 总点数，最终返回此数值的平方个点
    :return: 返回点集合list[float,float,float]，上限为1000个点
    """
    points=[]
    phi_values = [math.pi * i / (num_Sqr - 1) for i in range(num_Sqr)]
    theta_values = [2 * math.pi * i / num_Sqr for i in range(num_Sqr)]

    for phi in phi_values:
        for theta in theta_values:
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            points.append([x+center[0], y+center[1], z+center[2]])

    if len(points)>1000:
        print("请调小密度，为了保证性能，最多输出1000个点")
        return None
    else:
        return  points