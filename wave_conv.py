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
        
        # 24bitの場合は特別な処理が必要
        if sampwidth == 3:  # 24bit
            # 24bitデータを32bitとして読み込む
            # 3バイトを4バイトに拡張して読み込む必要がある
            num_samples = len(frames) // 3
            audio_data = np.zeros(num_samples, dtype=np.int32)
            
            # 24bitデータを32bitに変換
            for i in range(num_samples):
                # リトルエンディアンで3バイトを読み込み、符号を保持して32bitに拡張
                bytes_24 = frames[i*3:(i+1)*3] + (b'\x00' if frames[i*3+2] < 128 else b'\xff')
                audio_data[i] = int.from_bytes(bytes_24, byteorder='little', signed=True)
        else:
            # その他のビット深度の処理
            if sampwidth == 2:  # 16bit
                dtype = np.int16
            elif sampwidth == 1:  # 8bit
                dtype = np.int8
            elif sampwidth == 4:  # 32bit
                dtype = np.int32
            else:
                raise ValueError(f"Unsupported sample width: {sampwidth}")
            
            # バイトデータをnumpy配列に変換
            audio_data = np.frombuffer(frames, dtype=dtype)
        
        # ステレオの場合は適切に整形
        if channels == 2:
            audio_data = audio_data.reshape(-1, 2)
        
        # リサンプリング
        if framerate != target_rate:
            # 最大公約数を使用して適切な比率を計算
            gcd = np.gcd(framerate, target_rate)
            up = target_rate // gcd
            down = framerate // gcd
            
            # signal.resample_polyを使用してより高品質なリサンプリングを実行
            audio_data = signal.resample_poly(audio_data, up, down, axis=0)
            
            # float32からint16への変換時のスケーリングを調整
            if audio_data.dtype == np.float32:
                audio_data = np.int16(np.clip(audio_data * 32767, -32768, 32767))
        
        # 16bitに正規化
        if audio_data.dtype != np.int16:
            # データ型に応じてスケーリング
            if audio_data.dtype == np.int8:
                # 8bit (-128...127) から 16bit (-32768...32767) へ
                audio_data = audio_data.astype(np.float32) * 256
            elif audio_data.dtype == np.int32:
                # 24/32bit から 16bit へ
                # 24bitの場合は8ビット右シフト、32bitの場合は16ビット右シフト
                shift = 8 if sampwidth == 3 else 16
                audio_data = np.right_shift(audio_data, shift)
            
            # 範囲を16bitに制限
            audio_data = np.clip(audio_data, -32768, 32767).astype(np.int16)
        
        # 出力WAVファイルを作成
        with wave.open(output_path, 'wb') as wav_out:
            wav_out.setnchannels(channels)
            wav_out.setsampwidth(2)  # 16bit = 2bytes
            wav_out.setframerate(target_rate)
            wav_out.writeframes(audio_data.tobytes())

def main():
    if len(sys.argv) != 2:
        print("使用方法: python script.py <モード番号>")
        print("モード: 1 = 22050Hz, 2 = 44100Hz, 3 = 44100Hz")
        sys.exit(1)
    
    # モード番号から目標サンプリングレートを決定
    mode = int(sys.argv[1])
    target_rates = {
        1: 22050,  # Realtimeモード用
        2: 44100,  # Singingモード用
        3: 44100   # Testモード用
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
            
            try:
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
            except Exception as e:
                print(f"エラー ({file}): {str(e)}")
                continue

if __name__ == "__main__":
    main()