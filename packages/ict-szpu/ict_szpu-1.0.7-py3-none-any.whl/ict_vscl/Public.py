import time
import ict_szpu.core
from ict_szpu.core import MyWS


class audio:

    def __init__(self):
        pass

    def audio_load(self, file_name: str):
        """
        加载音频
        :param file_name:
        :return:
        """
        # MyWS.do_immediately(
        #     {'type': 'other', 'commond': 'audio_load', 'file_name': file_name})

        result =MyWS.do_wait_return( {'type': 'other', 'commond': 'audio_load', 'file_name': file_name})
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
        MyWS.do_immediately(
            {'type': 'other', 'commond': 'audio_play'})
        return

    def audio_pause(self):
        MyWS.do_immediately(
            {'type': 'other', 'commond': 'audio_pause'})
        return

    def audio_stop(self):
        MyWS.do_immediately(
            {'type': 'other', 'commond': 'audio_stop'})
        return

    def audio_set_volume(self):
        MyWS.do_immediately(
            {'type': 'other', 'commond': 'audio_set_volume'})
        return
