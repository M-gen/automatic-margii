
Automatic-Margii

===

アイキャッチや終了画面、BGMの合成をふくむ単純な動画をFFmpegを駆使することで
自動的に生成する

## Requirement

あらかじめFFmpegをインストールし、環境変数などの設定がすんでいること

確認しているFFmpegのバージョン
+ ffmpeg version git-2019-12-26-b0d0d7e

## Usage

### 大まかな手順

+ 素材の配置
   + ~/src_materials/bgm にBGM用のmp3を1つ配置する
   + ~/src_materials/end_movie に終了時のmp4を1つ配置する
   + ~/src_materials/eyecatch にmp4を1つ配置する
   + ~/src_movie に、動画本体のmp4を複数配置する

   main.pyのあるフォルダに src_materials と src_movie フォルダを作成し
   上記のように、素材を配置します

+ 結合
   + 下記のように main.py を実行する

   ```
   Python main.py --step_do "1 1 1 1" --e "1 2"
   ```
+ 出力される場所
   work フォルダが作成され、work/Step4/out.mp4 に結合したファイルが出力される

## Licence
[MIT](https://github.com/M-gen/automatic-margii/blob/master/LICENSE)

## Author

[えむげん](https://github.com/M-gen)