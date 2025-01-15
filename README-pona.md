## realtime_convesion.bat

リアルタイムボイチェン

## singing_voice_conversion.bat

歌声変換

## training.bat

トレーニング

- training_dataにwavファイルを入れてください
- training_data_convには、所定形式に変換済みの音声ファイルが入ります。
  realtime_conversionやsinging_voice_conversionを使うときには、このディレクトリに入った音声ファイルを使ってください
- 学習のepoch数が不足していると感じた場合には、同じモデル名で再度学習を実行すると、前回の学習結果の続きから再スタートできます。
  たとえば、1000epochで足りない場合に、もう1000epoch追加したいと考えた時に利用できます。
- その他バッチファイル内で表示されるメッセージに従って、設定を入力してください。

## reset.bat

環境をいったんクリーンにします

