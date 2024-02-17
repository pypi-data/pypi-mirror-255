import os

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesisResult


class TTSMicrosoft:
    def __init__(self, **kwargs) -> None:
        if not {"speech_key", "speech_region"}.issubset(kwargs.keys()):
            raise ValueError("speech_key,speech_region must be provided")
        self.speech_key = kwargs["speech_key"]
        self.speech_region = kwargs["speech_region"]

        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region,
        )

    def speak(self, text: str, audio_file: str) -> bool:
        """将文本转换为语音"""
        self.audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file)
        self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=self.audio_config
        )
        try:
            speech_synthesis_result: SpeechSynthesisResult = (
                self.speech_synthesizer.speak_text_async(text).get()
            )
            # print(speech_synthesis_result, type(speech_synthesis_result))
        except Exception as err:
            print(f"合成失败: {text}", err)
            return False
        return True
