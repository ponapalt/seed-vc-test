## run.bat

ボイスチェンジャー本体を実行します。

最初に以下の選択肢が出るので、適切なものを選んでください。

- Realtime Voice : リアルタイム音声変換 (seed-uvit-tat-xlsr-tiny)
- Voice : オフライン音声変換 (seed-uvit-whisper-small-wavenet)
- Singing : 歌声変換 (seed-uvit-whisper-base)

**Source Audio**に変換元の音声ファイルをドロップしてください。

また、必ず**Reference Audio**に学習に使った音声ファイルのうちどれか1つ（どれでもよい）をドロップしてください。

変換時にコンソールにたくさんエラーが出ますが、これらは無視できます。最終的に**Full Output Audioに再生ボタンが出たら成功**しています。

## training.bat

トレーニングを実行します。

以下の選択肢が出るので、適切なものを選んでください。

- Realtime Fine Tune : リアルタイム音声変換 (seed-uvit-tat-xlsr-tiny) + seed-vc標準モデルのファインチューニング
- Voice Fine Tune : オフライン音声変換 (seed-uvit-whisper-small-wavenet) + seed-vc標準モデルのファインチューニング
- Singing Fine Tune : 歌声変換 (seed-uvit-whisper-base) + seed-vc標準モデルのファインチューニング
- Full Scratch : 歌声変換 (seed-uvit-whisper-base) 向けにゼロからモデルをトレーニングする

その他注意点は以下の通りです。

- training_dataにwavファイルを入れてください
- training_data_convには、所定形式に変換済みの音声ファイルが入ります。
  realtime_conversionやsinging_voice_conversionを使うときには、このディレクトリに入った音声ファイルのうちどれか1つを、Reference Audioとして使ってください
- 学習のepoch数が不足していると感じた場合には、同じモデル名で再度学習を実行すると、前回の学習結果の続きから再スタートできます。
  たとえば、1000epochで足りない場合に、もう1000epoch追加したいと考えた時に利用できます。
- その他バッチファイル内で表示されるメッセージに従って、設定を入力してください。

## reset.bat

環境をいったん完全にクリーンにします

## update.bat

最新版にアップデートします

