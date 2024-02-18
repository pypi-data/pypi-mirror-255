import ict_szpu
from ict_szpu.core import MyWS

Number = 0


# 机器人
class Robot:
    name = '阿尔法狗'
    number = 0
    breast_piece_info = '编号2210'  # 胸牌信息
    color = '#ff00ff'

    def __init__(self,point: [float, float]=[0,0],rotate:float=0):
        """
        初始化
        :param point:初始坐标点 默认[0,0]
        :param rotate: 初始角度 默认0
        """
        global Number
        Number += 1
        self.number = Number
        result =MyWS.do_wait_return({'type': 'jqr', 'commond': 'init_position', 'point': point, 'rotate': rotate, 'number': self.number})
        if result['result'] == ict_szpu.core.SUCCESS:
            print(result['msg'])
            return
        else:
            print(result['msg'])
            return None

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
        :param color: 16进制颜色字符，如： #FFFFFF
        :return:
        """
        MyWS.do_immediately({'type': 'jqr', 'commond': 'set_color', 'color': color, 'number': self.number})
        return

    def servo_motor_control(self, servo_id: int, value: int):
        """
        舵机控制
        :param servo_id: 舵机id(1-18)
        :param value: 舵机值(0-1000)
        :return:
        """
        servo_id=int(servo_id)
        value=int(value)
        if (servo_id>=0 and servo_id<=18):
            if (value>=0 and value<=1000):
                MyWS.do_immediately({'type': 'jqr', 'commond': 'servo_motor_control', 'servo_id': servo_id, 'value': value,'number': self.number})
            else:
                print("舵机值设置错误：0-1000")
        else:
            print("舵机id设置错误:1-18")
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

    def play_action(self, action: str,loop_times=1, duration=0):
        """
        执行动作
        :param action:动作名称
        :param loop_times:动作循环次数 int,默认不重复
        :param duration:动作结束后等待时间秒 float,默认不等待
        :return:
        """
        MyWS.do_immediately({'type': 'jqr', 'commond': 'play_action', 'action': action, 'duration': duration, 'loop_times': loop_times,'number': self.number})
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

    def speak(self, txt: str, tone: str = 'xiaofeng'):
        """
        文本转语音
        :param txt:要转换的字符串
        :param tone:播音员（xiaofeng,xiaoyan,aisjiuxu,aisxping,aisjinger,aisbabyxu）
        :return:
        """
        MyWS.do_immediately({'type': 'jqr', 'commond': 'speak', 'number': self.number, 'txt': txt, 'tone': tone,'speed': 1})
        return

    def define_action(self):
        """
        打开动作编辑面板
        :param action:
        :return:
        """
        result = MyWS.do_wait_return({'type': 'jqr', 'commond': 'define_action', 'number': self.number})
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

    # def formation_control(self, point: [float, float], matrix_size: [int, int], matrix_direction: [float, float]):
    #     return
