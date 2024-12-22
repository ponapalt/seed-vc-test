import os
import sys
import wave
import shutil
from scipy import signal
import numpy as np

def get_wav_info(file_path):
    """WAVファイルの情報を取得する"""
    with wave.open(file_path, 'rb') as wav:
        return {
            'channels': wav.getnchannels(),
            'sampwidth': wav.getsampwidth(),
            'framerate': wav.getframerate(),
            'frames': wav.getnframes()
        }

def convert_wav(input_path, output_path, target_rate):
    """WAVファイルを指定のサンプリングレートに変換する"""
    # 入力WAVファイルを読み込む
    with wave.open(input_path, 'rb') as wav_in:
        # パラメータを取得
        channels = wav_in.getnchannels()
        sampwidth = wav_in.getsampwidth()
        framerate = wav_in.getframerate()
        
        # 音声データを読み込む
        frames = wav_in.readframes(wav_in.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16)
        
        if channels == 2:
            audio_data = audio_data.reshape(-1, 2)
        
        # リサンプリング
        if framerate != target_rate:
            # リサンプリング処理
            samples = len(audio_data)
            new_samples = int(samples * target_rate / framerate)
            audio_data = signal.resample(audio_data, new_samples)
        
        # 16bitに正規化
        audio_data = np.int16(audio_data)
        
        # 出力WAVファイルを作成
        with wave.open(output_path, 'wb') as wav_out:
            wav_out.setnchannels(channels)
            wav_out.setsampwidth(2)  # 16bit = 2bytes
            wav_out.setframerate(target_rate)
            wav_out.writeframes(audio_data.tobytes())

def main():
    if len(sys.argv) != 2:
        print("使用方法: python script.py <モード番号>")
        print("モード: 1 = 22050Hz, 2 = 44100Hz, 3 = 48000Hz")
        sys.exit(1)
    
    # モード番号から目標サンプリングレートを決定
    mode = int(sys.argv[1])
    target_rates = {
        1: 22050,
        2: 44100,
        3: 48000
    }
    
    if mode not in target_rates:
        print("無効なモード番号です")
        sys.exit(1)
    
    target_rate = target_rates[mode]
    
    # ディレクトリパスの設定
    input_dir = "training_data"
    output_dir = "training_data_conv"
    
    # training_data_conv内の全WAVファイルを削除
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.lower().endswith('.wav'):
                os.remove(os.path.join(output_dir, file))
    else:
        os.makedirs(output_dir)
    
    # training_data内のWAVファイルを処理
    for file in os.listdir(input_dir):
        if file.lower().endswith('.wav'):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file)
            
            # WAVファイルの情報を取得
            wav_info = get_wav_info(input_path)
            
            # 仕様チェック
            if (wav_info['framerate'] == target_rate and 
                wav_info['sampwidth'] == 2):  # 16bit = 2bytes
                # 仕様が一致する場合はコピー
                shutil.copy2(input_path, output_path)
                print(f"コピー: {file}")
            else:
                # 仕様が一致しない場合は変換
                convert_wav(input_path, output_path, target_rate)
                print(f"変換: {file}")

if __name__ == "__main__":
    main()