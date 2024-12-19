import os
import sys
from pydub import AudioSegment

def convert_audio(input_path, output_path, target_rate):
    """音声ファイルを指定のサンプリングレートに変換する"""
    try:
        # 音声ファイルを読み込む
        audio = AudioSegment.from_wav(input_path)
        
        # 30秒を超える音声ファイルはスキップ
        if audio.duration_seconds > 30:
            print(f"スキップ: {os.path.basename(input_path)} (長さ: {audio.duration_seconds:.1f}秒)")
            return False
        
        # サンプリングレートとビット深度をチェック
        if audio.frame_rate != target_rate or audio.sample_width != 2:  # 2 bytes = 16bit
            # サンプリングレートとビット深度を変換
            audio = audio.set_frame_rate(target_rate).set_sample_width(2)
        
        # 変換した音声を保存
        audio.export(output_path, format='wav')
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
    error_files = 0
    skipped_files = 0
    
    for file in os.listdir(input_dir):
        if file.lower().endswith('.wav'):
            total_files += 1
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file)
            
            try:
                # 音声ファイルを読み込んでチェック
                audio = AudioSegment.from_wav(input_path)
                
                # 30秒を超える音声ファイルはスキップ
                if audio.duration_seconds > 30:
                    print(f"スキップ: {file} (長さ: {audio.duration_seconds:.1f}秒)")
                    skipped_files += 1
                    continue
                
                if audio.frame_rate == target_rate and audio.sample_width == 2:
                    # 仕様が一致する場合は直接コピー
                    audio.export(output_path, format='wav')
                    print(f"コピー完了: {file}")
                else:
                    # 仕様が一致しない場合は変換
                    if convert_audio(input_path, output_path, target_rate):
                        print(f"変換完了: {file} ({audio.frame_rate}Hz -> {target_rate}Hz)")
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
    print(f"変換完了: {converted_files}")
    print(f"エラー: {error_files}")
    print(f"スキップ (30秒超): {skipped_files}")
    print(f"コピー: {total_files - converted_files - error_files - skipped_files}")

if __name__ == "__main__":
    main()