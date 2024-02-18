import time

import ict_szpu.core
from ict_szpu.core import MyWS

Number = 0
Time = time.strftime('%H:%M:%S', time.localtime(time.time()))


# 无人机
class UAV:
    # 编号
    number = 0
    # 名称
    name = ''
    # 无人机区域1、2颜色
    color_1 = ''
    color_2 = ''
    # 位置
    pos_x = 0
    pos_y = 0
    # 旋翼输出
    rotor_power = [0, 0, 0, 0]
    # 灯光颜色
    lighter_color = ''
    # 高度
    height = 0
    # 水平距离
    distance = 0
    # 姿态角
    attitude_angle = [0, 0, 0]
    # 水平速度
    horizontal_speed = 0
    # 垂直速度
    vertical_speed = 0

    # def __init__(self, point: [float, float]):
    #     """
    #     无人机构造函数
    #     :param point: 设置无人机生成位置
    #     """
    #     global Number
    #     Number += 1
    #     self.number = Number
    #     self.pos_x = point[0]
    #     self.pos_y = point[1]
    #     result = MyWS.doAwait({'type': 'wrj', 'commond': 'create', 'pos': point, 'number': self.number})
    #     if (result['result'] == ict_szpu.core.SUCCESS):
    #         print('创建成功:' + str(self.number))

    def __init__(self):
        pass

    def init_position(self, point: [float, float]):
        """
        初始化无人机坐标
        :param point:
        :return:
        """
        global Number
        Number += 1
        self.number = Number
        self.pos_x = point[0]
        self.pos_y = point[1]
        result = MyWS.do_wait_return({'type': 'wrj', 'commond': 'init_position', 'pos': point, 'number': self.number})
        if result['result'] == ict_szpu.core.SUCCESS:
            print('【%s UAV:%s】创建成功，事件%s结束' % (Time, self.number, result['event_id']))
        return self

    def set_name(self, name: str):
        """
        设置无人机名称
        :param name:无人机名称
        :return:
        """
        self.name = name
        # result = MyWS.do_wait_return({'type': 'wrj', 'commond': 'set_name', 'name': name, 'number': self.number})
        # if result['result'] == ict_szpu.core.SUCCESS:
        #     print('【%s UAV:%s】创建成功，事件%s结束' % (Time, self.number, result['event_id']))
        MyWS.do_immediately({'type': 'wrj', 'commond': 'set_name', 'name': name, 'number': self.number})
        return

    def set_color(self, color_1: str = '#FFFFFF', color_2: str = '#000000'):
        """
        设置无人机颜色
        :param color_1:无人机模型区域1颜色
        :param color_2:无人机模型区域2颜色
        :return:
        """
        self.color_1 = color_1
        self.color_2 = color_2
        MyWS.do_immediately(
            {'type': 'wrj', 'commond': 'set_color', 'color_1': color_1, 'color_2': color_2, 'number': self.number})
        return

    def start_engine(self):
        """
        启动引擎
        :return:
        """
        # result = MyWS.do_wait_return({'type': 'wrj', 'commond': 'start_engine', 'number': self.number})
        # if result['result'] == ict_szpu.core.SUCCESS:
        #     print('【%s UAV:%s】启动成功，事件%s结束' % (Time, self.number, result['event_id']))
        MyWS.do_immediately({'type': 'wrj', 'commond': 'start_engine', 'number': self.number})
        return

    def shut_down_engine(self):
        """
        关闭引擎
        :return:
        """
        # result = MyWS.do_wait_return({'type': 'wrj', 'commond': 'shut_down_engine', 'number': self.number})
        # if result['result'] == ict_szpu.core.SUCCESS:
        #     print('【%s UAV:%s】关闭成功，事件%s结束' % (Time, self.number, result['event_id']))
        MyWS.do_immediately({'type': 'wrj', 'commond': 'shut_down_engine', 'number': self.number})
        return

    def set_rotor_power(self, power: [float, float, float, float]):
        """
        设置无人机各旋翼输出
        :param power:
        :return:
        """
        self.rotor_power = power
        MyWS.do_immediately(self.__handle_result('set_rotor_power', {'power': power}))
        return

    def open_lighter(self, color: str, intensity: float = 1, halo: float = 1):
        """
        打开无人机灯光
        :param color: 灯光颜色
        :param intensity: 灯光强度
        :param halo: 光晕强度
        :return:
        """
        self.lighter_color = color
        MyWS.do_immediately(
            self.__handle_result('open_lighter', {'color': color, 'intensity': intensity, 'halo': halo}))
        return

    def close_lighter(self):
        """
        关闭无人机灯光
        :return:
        """
        MyWS.do_immediately(self.__handle_result('close_lighter'))
        return

    def get_current_height(self):
        """
        获取无人机当前高度
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('get_current_height'))
        if result['result'] == ict_szpu.core.SUCCESS:
            print(result['msg'])
        return

    def get_current_attitude_angle(self):
        """
        获取无人机当前姿态角
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('get_current_attitude_angle'))
        if result['result'] == ict_szpu.core.SUCCESS:
            print(result['msg'])
        return

    def get_current_distance(self):
        """
        当前无人机与返航点的水平方向距离
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('get_current_distance'))
        if result['result'] == ict_szpu.core.SUCCESS:
            print(result['msg'])
        return

    def get_current_horizontal_speed(self):
        """
        当前无人机的水平方向速度
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('get_current_horizontal_speed'))
        if result['result'] == ict_szpu.core.SUCCESS:
            print(result['msg'])
        return

    def get_current_vertical_speed(self):
        """
        当前无人机的垂直速度
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('get_current_vertical_speed'))
        if result['result'] == ict_szpu.core.SUCCESS:
            print(result['msg'])
        return

    def open_hd(self):
        """
        打开高清图传
        :return:
        """
        MyWS.do_immediately(self.__handle_result('open_hd'))
        return

    def close_hd(self):
        """
        关闭高清图传
        :return:
        """
        MyWS.do_immediately(self.__handle_result('close_hd'))
        return

    def fly_by_3d_direction(self, direction: [float, float, float], speed: float, duration: float):
        """
        以给定速度朝方向飞行多长时间
        :param direction: 三维飞行方向，X：前后，Y：左右，Z：上下
        :param speed: 飞行速度（米/秒）
        :param duration: 飞行时间（秒）
        :return:
        """
        MyWS.do_immediately(
            {'type': 'wrj', 'commond': 'fly_by_3d_direction', 'number': self.number, 'direction': direction,
             'speed': speed,
             'time': duration}
        )
        return

    def fly_to_point_by_time(self, direction: [float, float, float], duration: float, wait_for_return: bool = False):
        """
        在规定时间内飞至指定位置
        :param direction: 目标点坐标
        :param duration: 固定时间（秒）
        :param wait_for_return: 是否等待Unity程序返回结果
        :return:
        """
        if wait_for_return:
            result = MyWS.do_wait_return(
                {'type': 'wrj', 'commond': 'fly_to_point_by_time', 'number': self.number, 'direction': direction,
                 'duration': duration})
            if result['result'] == ict_szpu.core.SUCCESS:
                # print('【%s UAV:%s】飞行完成，事件%s结束' % (Time, self.number, result['event_id']))
                return
        else:
            MyWS.do_immediately(
                {'type': 'wrj', 'commond': 'fly_to_point_by_time', 'number': self.number, 'direction': direction,
                 'duration': duration})
        return

    def fly_to_point_by_speed(self, direction: [float, float, float], speed: float):
        """
        在固定速度的情况下飞至指定位置
        :param direction: 目标点坐标
        :param speed: 飞行速度（米/秒）
        :return:
        """
        MyWS.do_immediately(
            {'type': 'wrj', 'commond': 'fly_to_point_by_speed', 'number': self.number, 'direction': direction,
             'duration': speed}
        )
        # if result['result'] == ict_szpu.core.SUCCESS:
        #     print('【%s UAV:%s】飞行完成，事件%s结束' % (Time, self.number, result['event_id']))
        return

    def hovering(self):
        """
        无人机悬停
        :return:
        """
        MyWS.do_immediately(self.__handle_result('hovering'))
        return

    def open_trail_render(self, color: str = '#FFFFFF', thickness: float = 0.1):
        """
        打开无人机飞行轨迹
        :param color: 轨迹颜色
        :param thickness: 轨迹厚度，[0.1-1]
        :return:
        """
        MyWS.do_immediately(
            self.__handle_result('open_trail_render', {'color': color, 'thickness': thickness})
        )
        return

    def close_trail_render(self):
        """
        关闭无人机飞行轨迹
        :return:
        """
        MyWS.do_immediately(
            {'type': 'wrj', 'commond': 'close_trail_render', 'number': self.number}
        )
        return

    def enable_obstacle_avoidance(self):
        """

        :return:
        """
        MyWS.do_immediately({'type': 'wrj', 'commond': 'enable_obstacle_avoidance', 'number': self.number})
        return

    def disable_obstacle_avoidance(self):
        """

        :return:
        """
        MyWS.do_immediately({'type': 'wrj', 'commond': 'disable_obstacle_avoidance', 'number': self.number})
        return

    def __handle_result(self, commond: str, parameters: dict = None):
        # for i in parameters:

        return {'type': 'wrj', 'commond': commond, 'number': self.number, 'parameters': parameters}

    def formation_control(self, formation_data: [str], wait_for_return: bool = False):
        """

        :param formation_data: 编队数据
        :param wait_for_return: 是否等待程序执行结束
        :return:
        """
        data = {'type': 'wrj', 'commond': 'formation_control', 'formation_data': formation_data,
                'wait_for_return': wait_for_return}
        if wait_for_return:
            result = MyWS.do_wait_return(data)
            if result['result'] == ict_szpu.core.SUCCESS:
                return
        else:
            MyWS.do_immediately(data)
            return

    def time_set(self, t_time: str = '昼'):
        """

        :param t_time:时间：昼、夜
        :return:
        """
        data = {'type': 'wrj', 'commond': 'time_set', 't_time': t_time}
        result = MyWS.do_wait_return(data)
        if result['result'] == ict_szpu.core.SUCCESS:
            print('设置成功')
            return
        else:
            print('设置失败')
            return

    def open_real_camera(self):
        """

        :return:
        """
        MyWS.do_immediately(self.__handle_result('open_real_camera'))

    def close_real_camera(self):
        """

        :return:
        """
        MyWS.do_immediately(self.__handle_result('close_real_camera'))
    def get_speech_text(self):
        """
        开始语音识别，并获取语音识别结果
        :return:
        """
        result = MyWS.do_wait_return({'type': 'wrj', 'commond': 'get_speech_text', 'number': self.number})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']
        else:
            print(result['msg'])
            return None