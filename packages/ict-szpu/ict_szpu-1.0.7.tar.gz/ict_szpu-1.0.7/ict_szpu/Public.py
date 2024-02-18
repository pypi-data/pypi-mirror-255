import json
import time
import ict_szpu.core
from ict_szpu.core import MyWS


class audio:

    def __init__(self):
        pass

    def audio_load(self, filepath: str):
        """
        加载音频  (仅支持wav，mp3格式)
        :param filepath:文件路径
        :return: 返回成功：True或失败：False
        """
        # MyWS.do_immediately(
        #     {'type': 'other', 'commond': 'audio_load', 'file_name': file_name})

        result =MyWS.do_wait_return( {'type': 'other', 'commond': 'audio_load', 'filepath': filepath})
        if result['result'] == ict_szpu.core.SUCCESS:
            return True
        else:
            print(result['msg'])
            return False

    def audio_play(self):
        """
        播放音频
        :return:
        """
        MyWS.do_immediately({'type': 'other', 'commond': 'audio_play'})
        return

    def audio_pause(self):
        """
        暂停音频播放
        :return:
        """
        MyWS.do_immediately({'type': 'other', 'commond': 'audio_pause'})
        return

    def audio_stop(self):
        """
        停止播放音频
        :return:
        """
        MyWS.do_immediately({'type': 'other', 'commond': 'audio_stop'})
        return

    def audio_set_volume(self,volume:float):
        """
        设置音量
        :param volume: 音量大小(0~1)
        :return:
        """
        MyWS.do_immediately({'type': 'other', 'commond': 'audio_set_volume','volume':volume})
        return


def screen_shot(isStep:bool, stepName:str=''):
    """
    截图
    :param isStep: False:整个任务截图，True:单个步骤截图
    :param stepName: 填写对应步骤名，用于对应步骤
    :return:
    """
    if isStep==True:
        if stepName=='':
            print('截图步骤时步骤名称不能为空')
            return

    MyWS.do_immediately({'type': 'other', 'commond': 'screen_shot','isStep':isStep,'stepName':stepName})
    return

def set_camera_mode(mode:str,center:[float,float,float]=None,radius:float=None,speed:float=None,high:float=None):
    """
    设置相机模式
    :param mode: 模式名：自由模式 或 环绕模式
    :param center: 环绕中点
    :param radius: 环绕半径
    :param speed: 环绕速度
    :return:
    """
    if mode=='自由模式':
        MyWS.do_immediately({'type': 'other', 'commond': 'set_camera_mode', 'mode': mode})
    elif mode=='环绕模式':
        if(center==None or radius==None or speed==None or high==None):
            print('环绕模式下，请设置其它参数')
        else:
            MyWS.do_immediately({'type': 'other', 'commond': 'set_camera_mode', 'mode': mode,'center': center,'radius': radius,'speed': speed,'high':high})
    else:
        print('请输入正确模式名称')
    return

def get_control_image():
    """
    获取当前场景可替换的所有照片
    :return: 返回照片名称数组 string[]
    """
    result=MyWS.do_wait_return({'type': 'other', 'commond': 'get_control_image'})
    if result['result'] == ict_szpu.core.SUCCESS:
        return json.loads(result['msg'])
    else:
        print(result['msg'])
        return None

def set_control_image(bgName:str,filePath:str):
    """
    设置背景照片
    :param bgName: 照片名称
    :param filePath: 图片本地路径
    :return:True:设置成功，False:设置失败
    """
    result=MyWS.do_wait_return({'type': 'other', 'commond': 'set_control_image', 'name': bgName,'filePath':filePath})
    if result['result'] == ict_szpu.core.SUCCESS:
        return True
    else:
        print("照片设置失败："+result['msg'])
        return False

def get_scene_objet():
    """
    获取可创建的场景元素物体
    :return:返回元素名称数组 string[]
    """
    result = MyWS.do_wait_return({'type': 'other', 'commond': 'get_scene_objet'})
    if result['result'] == ict_szpu.core.SUCCESS:
        return json.loads(result['msg'])
    else:
        print(result['msg'])
        return None
def set_scene_objet(name:str,point: [float, float,float]=[0,0,0],rotate:[float,float,float]=[0,0,0]):
    """
    创建场景元素物体
    :param name:物体名
    :param point:坐标位置
    :param rotate:旋转角度
    :return:True:设置成功，False:设置失败
    """
    result = MyWS.do_wait_return({'type': 'other', 'commond': 'set_scene_objet', 'name': name, 'point': point,'rotate':rotate})
    if result['result'] == ict_szpu.core.SUCCESS:
        return True
    else:
        print("场景元素设置失败："+result['msg'])
        return False


