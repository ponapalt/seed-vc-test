import os
import sys
import shutil
import soundfile as sf
import librosa

def get_audio_info(file_path):
    """音声ファイルの情報を取得する"""
    try:
        info = sf.info(file_path)
        return {
            'samplerate': info.samplerate,
            'channels': info.channels,
            'subtype': info.subtype,  # フォーマット情報（例：'PCM_16'）
            'frames': info.frames
        }
    except Exception as e:
        print(f"Error reading file info: {str(e)}")
        return None

def convert_audio(input_path, output_path, target_rate):
    """音声ファイルを指定のサンプリングレートに変換する"""
    try:
        # librosaで音声を読み込む（自動的にfloat32、モノラル化される）
        audio, sr = librosa.load(input_path, sr=None, mono=False)
        
        # ステレオの場合は転置して正しい形式にする
        if len(audio.shape) == 2 and audio.shape[0] == 2:
            audio = audio.T

        # サンプリングレートの変換が必要な場合
        if sr != target_rate:
            # librosaのresampleを使用（高品質なリサンプリング）
            audio = librosa.resample(
                y=audio,
                orig_sr=sr,
                target_sr=target_rate,
                res_type='kaiser_best'  # 最高品質の設定
            )

        # ステレオの場合は元の形式に戻す
        if len(audio.shape) == 2 and audio.shape[1] == 2:
            audio = audio.T

        # 16bitの範囲にクリッピング
        audio = audio * 32767
        audio = audio.clip(-32768, 32767)

        # 16bit PCMとして保存
        sf.write(
            output_path,
            audio,
            target_rate,
            subtype='PCM_16',
            format='WAV'
        )
        return True

    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False

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
    total_files = 0
    converted_files = 0
    copied_files = 0
    error_files = 0
    
    for file in os.listdir(input_dir):
        if file.lower().endswith('.wav'):
            total_files += 1
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file)
            
            # 音声ファイルの情報を取得
            info = get_audio_info(input_path)
            if info is None:
                error_files += 1
                continue
            
            try:
                # サンプリングレートとビット深度をチェック
                if info['samplerate'] == target_rate and info['subtype'] == 'PCM_16':
                    # 仕様が一致する場合はコピー
                    shutil.copy2(input_path, output_path)
                    print(f"コピー完了: {file}")
                    copied_files += 1
                else:
                    # 仕様が一致しない場合は変換
                    if convert_audio(input_path, output_path, target_rate):
                        print(f"変換完了: {file}")
                        converted_files += 1
                    else:
                        print(f"変換失敗: {file}")
                        error_files += 1
            
            except Exception as e:
                print(f"エラー ({file}): {str(e)}")
                error_files += 1
                continue
    
    # 処理結果のサマリーを表示
    print("\n処理完了サマリー:")
    print(f"総ファイル数: {total_files}")
    print(f"コピー完了: {copied_files}")
    print(f"変換完了: {converted_files}")
    print(f"エラー: {error_files}")

if __name__ == "__main__":
    main()