import io
from fastapi import FastAPI, HTTPException
import requests
import base64
from pydub import AudioSegment
import random

app = FastAPI()


@app.get("/")
async def index():
    return {"message": "Hello World"}


@app.get("/api/tts")
async def text_to_speech(
    text: str,
    voice: str = "zh-CN-YunyangNeural",
    formart: str = "mp3",
):
    try:
        # 准备请求数据
        url = "https://www.text-to-speech.cn/getSpeek.php"
        headers = {
            "authority": "www.text-to-speech.cn",
            "pragma": "no-cache",
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        }
        data = {
            "language": "中文（普通话，简体）",
            "voice": voice,
            "text": text,
            "role": "0",
            "style": "0",
            "styledegree": "1",
            "volume": "75",
            "predict": "0",
            "rate": "0",
            "pitch": "0",
            "kbitrate": "audio-16khz-32kbitrate-mono-mp3",
            "silence": "",
            "user_id": "",
            "yzm": "202410170001",
        }

        # 发送请求获取MP3链接
        response = requests.post(url, headers=headers, data=data)
        result = response.json()

        if result["code"] != 200:
            raise HTTPException(status_code=400, detail="TTS服务请求失败")

        # 下载MP3文件并转换为base64
        mp3_response = requests.get(result["download"])
        voice_base64 = ""
        if formart == "mp3":
            voice_base64 = base64.b64encode(mp3_response.content).decode()
        elif formart == "amr":
            audio = AudioSegment.from_file(
                io.BytesIO(mp3_response.content), format="mp3"
            )
            audio = audio.set_frame_rate(8000)  # 设置采样率为8000Hz

            # 将音频转换为 AMR 格式并获取 base64
            amr_buffer = io.BytesIO()
            audio.export(amr_buffer, format="amr")
            voice_base64 = base64.b64encode(amr_buffer.getvalue()).decode()

        return {
            "code": 200,
            "data": {"base64": voice_base64, "url": result["download"]},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 音色 https://www.text-to-speech.cn/getSpeekList.php
@app.get("/api/tts/voices")
async def get_voices():
    url = "https://www.text-to-speech.cn/getSpeekList.php"
    response = requests.get(url)
    return {"code": 200, "data": response.json()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
