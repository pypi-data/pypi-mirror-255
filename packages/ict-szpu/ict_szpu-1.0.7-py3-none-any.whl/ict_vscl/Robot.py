import ict_szpu
from ict_szpu.core import MyWS

Number = 0


# 机器人
class Robot:
    name = '阿尔法狗'
    number = 0
    breast_piece_info = '编号2210'  # 胸牌信息
    color = '#ff00ff'

    def __init__(self):
        pass

    def init_position(self, point: [float, float],rotate:float=0):
        """
        初始化机器人位置
        :param point:
        :return:
        """
        global Number
        Number += 1
        self.number = Number
        MyWS.do_immediately({'type': 'jqr', 'commond': 'init_position', 'point': point,'rotate':rotate, 'number': self.number})
        return

    def set_name(self, name: str):
        """
        设置机器人名称
        :param name:
        :return:
        """
        self.name = name
        MyWS.do_immediately({'type': 'jqr', 'commond': 'set_name', 'name': name, 'number': self.number})
        return

    def set_color(self, color: str):
        """
        设置机器人颜色
        :param color:
        :return:
        """
        MyWS.do_immediately({'type': 'jqr', 'commond': 'set_color', 'color': color, 'number': self.number})
        return

    def servo_motor_control(self, servo_id: int, value: int):
        """
        舵机控制
        :param servo_id: 舵机id
        :param value: 舵机值
        :return:
        """
        MyWS.do_immediately({'type': 'jqr', 'commond': 'servo_motor_control', 'servo_id': servo_id, 'value': value,
                             'number': self.number})
        return

    def get_action_lab(self):
        """
        获取机器人所有动作
        :return:
        """
        result = MyWS.do_wait_return({'type': 'jqr', 'commond': 'get_action_lab', 'number': self.number})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']
        else:
            print(result['msg'])
            return None

    def play_action(self, action: str, duration=0, loop_times=1):
        """
        执行动作
        :param action:动作名称
        :param duration:持续时间 float
        :param loop_times:循环次数 int
        :return:
        """
        MyWS.do_immediately(
            {'type': 'jqr', 'commond': 'play_action', 'action': action, 'duration': duration, 'loop_times': loop_times,
             'number': self.number})
        return

    def get_speech_text(self):
        """
        开始语音识别，并获取语音识别结果
        :return:
        """
        result = MyWS.do_wait_return({'type': 'jqr', 'commond': 'get_speech_text', 'number': self.number})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']
        else:
            print(result['msg'])
            return None

    def speak(self, txt: str, tone: str = '机器人', speed: int = 0, save: bool = False, file_name: str = ''):
        """
        文本转语音
        :param txt:
        :param tone:
        :param speed:
        :param save:
        :param file_name:
        :return:
        """
        MyWS.do_immediately({'type': 'jqr', 'commond': 'speak', 'number': self.number, 'txt': txt, 'tone': tone,
                             'speed': speed, 'save': save, 'file_name': file_name})
        return

    def define_action(self):
        """
        打开动作编辑面板
        :param action:
        :return:
        """
        result = MyWS.do_wait_return(
            {'type': 'jqr', 'commond': 'define_action', 'number': self.number})
        if result['result'] == ict_szpu.core.SUCCESS:
            print(result['msg'])
        return
    def open_colorDetect(self):
        """
        打开图像识别
        """
        MyWS.do_immediately({'type': 'jqr', 'commond': 'openColorDetect', 'number': self.number})
        return

    def stop_colorDetect(self):
        """
        停止图像识别
        """
        MyWS.do_immediately({'type': 'jqr', 'commond': 'stopColorDetect', 'number': self.number})
        return

    def formation_control(self, point: [float, float], matrix_size: [int, int], matrix_direction: [float, float]):
        return


def init_robot():
    """
    创建一个机器人
    :return: 返回一个机器人对象
    """
    robot = Robot()
    return robot
