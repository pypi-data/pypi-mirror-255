import ict_szpu.core
from ict_szpu.core import MyWS

# 数字人
class DigtalHuman():
    name = '安琪拉'
    age = 18
    sex = False  # 性别 true：男 ，false：女
    build = []  # 体型
    complexion = []  # 肤色
    voice = []  # 声音
    volume = 1.0  # 音量
    appearance = []  # 容貌
    clothing_lab = ['西装男', '西装女', '古装男', '古装女']  # 服装
    expression = []  # 表情
    head_action = []  # 头部动作
    hand_action = []  # 手部动作
    Legsandtorso_action = []  # 腿和躯干动作
    default_action = []  # 默认动作无法定制

    def __init__(self):
        """

        """
        MyWS.do_wait_return({'type': 'szr', 'commond': 'init'})
        return

    # def init_man(self):
    #     return self

    def init_human(self, sex: str):
        """
        初始化数字人
        :param sex:性别Male，Female
        :return: self
        """

        result = MyWS.do_wait_return(self.__handle_result('init_human', {'sex': sex}))
        return self

    def set_name(self, name: str):
        """
        设置数字人名字
        :param name:名称
        :return: bool返回操作成功或失败
        """

        result = MyWS.do_wait_return(self.__handle_result('set_name', {'name': name}))
        return result['msg']

    def set_age(self, age: int):
        """
        设置数字人年龄
        :param age:年龄
        :return: bool返回操作成功或失败
        """

        result = MyWS.do_wait_return(self.__handle_result('set_age', {'age': age}))
        return result['msg']

    def get_sex(self):
        """
        获取数字人性别
        :return:返回性别
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_sex'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def set_sex(self, sex: str):
        """
        设置数字人性别
        :param sex:性别Male，Female
        :return: bool返回操作成功或失败
        """

        result = MyWS.do_wait_return(self.__handle_result('set_sex', {'sex': sex}))
        return result['msg']

    def get_somatotype(self):
        """
        获取体型列表
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_somatotype'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def set_somatotype(self, somatotype: str):
        """
        设置体型
        :param somatotype:体型
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_somatotype', {'somatotype': somatotype}))
        return result['msg']

    def set_volume(self, volume: int):
        """
        设置音量
        :param volume:音量
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_volume', {'volume': volume}))
        return result['msg']
        return

    def get_clothing(self):
        """
        获取服装列表
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_clothing'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def set_clothing(self, clothing: str):
        """
        设置服装
        :param clothing:服装
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_clothing', {'clothing': clothing}))
        return result['msg']

    def get_hairstyle(self):
        """
        获取发型列表
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_hairstyle'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def set_hairstyle(self, hairstyle: str):
        """
        设置发型
        :param hairstyle: 发型
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_hairstyle', {'hairstyle': hairstyle}))
        return result['msg']

    def get_face(self):
        """
        获取脸型列表
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_face'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def set_face(self, face: str):
        """
        设置脸型
        :return: face: 脸型
        """
        result = MyWS.do_wait_return(self.__handle_result('set_face', {'face': face}))
        return result['msg']

    def get_glasses(self):
        """
        获取眼镜列表
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_glasses'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def set_glasses(self, glasses: str):
        """
        设置眼镜
        :return: glasses : 眼镜
        """
        result = MyWS.do_wait_return(self.__handle_result('set_glasses', {'glasses': glasses}))
        return result['msg']

    def __handle_result(self, commond: str, parameters: dict = None):
        # for i in parameters:
        return {'type': 'szr', 'commond': commond, 'parameters': parameters}

    def get_head_action(self):
        """
        获取头部动作列表
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_head_action'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def get_hand_action(self):
            """
            获取手部动作列表
            :return:
            """
            result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_hand_action'})
            if result['result'] == ict_szpu.core.SUCCESS:
                return result['msg']

    def get_legs_action(self):
            """
            获取腿部动作列表
            :return:
            """
            result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_legs_action'})
            if result['result'] == ict_szpu.core.SUCCESS:
                return result['msg']

    def get_torso_action(self):
            """
            获取躯干动作列表
            :return:
            """
            result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_torso_action'})
            if result['result'] == ict_szpu.core.SUCCESS:
                return result['msg']

    def get_emote_action(self):
            """
            获取表情动作列表
            :return:
            """
            result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_emote_action'})
            if result['result'] == ict_szpu.core.SUCCESS:
                return result['msg']

    def set_head_action(self, action: [str], loop_times: int):
        """
        设置头部动作
        :param action:
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_head_action', {'action': action,'loop_times': loop_times}))
        return result['msg']

    def set_hand_action(self, action: [str], loop_times: int):
        """
        设置手部动作
        :param action:
        :param loop_times:
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_hand_action', {'action': action,'loop_times': loop_times}))
        return result['msg']

    def set_torso_action(self, action: [str], loop_times: int):
        """
        设置躯干动作
        :param action:
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_torso_action', {'action': action,'loop_times': loop_times}))
        return result['msg']

    def set_emote_action(self, emote: str):
        """
        设置表情动作
        :param action:
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_emote_action', {'emote': emote}))
        return result['msg']

    def get_skincolor(self):
        """
        获取肤色列表
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_skincolor'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def set_skincolor(self, skincolor: str):
        """
        设置肤色
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_skincolor', {'skincolor': skincolor}))
        return result['msg']

    def get_timbre(self):
        """
        获取音色列表
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'get_timbre'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def set_timbre(self, timbre: str):
        """
        设置音色
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('set_timbre', {'timbre': timbre}))
        return result['msg']

    def stop_audio(self):
        """
        停止音乐
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'stop_audio'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def play_text_content(self, content: str):
        """
        播报新闻稿
        :param content:
        :return:
        """
        result = MyWS.do_wait_return(self.__handle_result('play_text_content', {'content': content}))
        return result['msg']

    def stop_text(self):
        """
        停止播报新闻稿
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'stop_text'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']

    def export_appearance(self):
        """
        导出外观参数
        :return:
        """
        result = MyWS.do_wait_return({'type': 'szr', 'commond': 'export_appearance'})
        if result['result'] == ict_szpu.core.SUCCESS:
            return result['msg']