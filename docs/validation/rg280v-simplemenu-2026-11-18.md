# SimpleMenuとSimple Questの導入（2026-11-18）

## 実機の状態と操作

plumOSのSTART → Apps → **SimpleMenu** から起動する。既存のplumOS FEは起動時の既定のまま。

- A: 決定・ゲーム起動、B: 戻る。
- ROM一覧でSELECT: ゲーム別のエミュ選択。`Default` は現在のplumOS FEの選択・ROM別設定を使う。
- START → Themeを左右で切替 → B: テーマ変更を反映。
- START → Sessionを`quit`にしてA: SimpleMenuを終了し、plumOSのAppsへ戻る。

有効なFEの26機種を4グループへ登録し、既定と明示指定を合わせた84本の起動スクリプトを生成した。ROMはSD2の通常ディレクトリを直接走査する。新しいROMを置く際にコピーやシンボリックリンク一覧の再作成は不要。エミュ本体は既存の正規FE経路を使い、RA等の拒否済み経路を新たに登録しない。

Appsに残っていた`rg350_`で始まる検証用の入口53件は削除。通常OPKアプリと、正規登録したエミュは保持した。旧Apps設定のバックアップは `/media/data/plumos/backup/simplemenu-20261118/apps.json`。検証用OPKの実体・ROM・セーブの一括削除はしていない。

## 使用元とテーマ

- [fgl82/SimpleMenu](https://github.com/fgl82/simplemenu)、リビジョン `e70a861b1f05fd83cd1b19be53be11c0a0ecd510`。
- コードはGPL-3.0。上流の画像素材はREADMEに記載されたCC BY-NC-SAを参照。実機のruntimeにライセンスと上流READMEを同梱。
- [作者のSimple Quest配布ページ](https://yoshives.com/simplemenu-theme-simple-quest/)から320×240版を取得。SimpleQuestとSimpleQuest2を両方導入し、元の画像・フォント・theme.iniは改変していない。
- 配布ZIPのSHA-256: `b30d4fdae5fa5fde5e6d559e13848c4477adbb1a3de2d22237c8f454a27b81e6`。

作者はテーマの改変を認める一方で再配布を禁止している。ZIPや展開したテーマはGit管理外の`output/rg280v-simplemenu/`と、この実機のSD1だけに置く。公開用OSイメージ・公開リリースへの同梱対象にはしない。

## 移植内容

- RG280Vのsoft-float ABIでSDL 1.2向けにソースからビルド。既存のkmsdrmバックエンドで論理320×240を表示する。
- RG350専用の振動処理、VTリセット、表示モードの再初期化と640×480の自動選択をこのターゲットで無効化。共通SDL・ALSA・カーネルは変更していない。
- 起動時にセクションの解放後のポインタをinvokerへ渡していた問題を修正。エミュディレクトリとROMパスを解放前に複製し、空のstate引数も正しく終端する。
- 専用invokerは登録済み起動スクリプトだけを実行し、エミュ終了後は保存した位置でSimpleMenuを再起動する。ファイル名をシェルのコマンド文字列へ連結しない。
- 文字描画をUTF-8対応へ変更し、切り詰めをコードポイント境界で行う。テーマフォントにない漢字・空白グリフは、既存の`plumos/fonts/cjk-fallback.ttc`へ行単位でフォールバックする。収録済みの文字は元のテーマフォントを使う。
- SimpleMenuからCPU周波数を変更せず、既存のplumOSの996MHz上限・governorを維持。ゲーム別画面は`CPU policy: plumOS`と表示する。旧ODの起動スクリプト置換は無効化し、Default launcher項目にplumOSが起動を管理する旨のヒントを表示する。
- SimpleMenu側のreboot/shutdownも既存の`plumos-safe-shutdown`へ接続。Sessionの既定はquit。
- `.discs`などの隠しディレクトリをROM走査から除き、CDのトラック実体を通常のROMとして重複表示しない。
- HOMEはSD1の`plumos/home/simplemenu`。テーマ選択・一覧位置・お気に入り・ゲーム別設定をここへ保存する。通常時の詳細デバッグログはOFF。

## 実機で確認した内容

1. plumOSのAppsにSimpleMenuが表示され、検証用TEST経路がなくなっている。
2. AppsからSimple Questを起動し、機種選択とROM一覧の表示・入力を確認。
3. Simple QuestからSA FCEUX 2.2.3で悪魔城伝説を起動。取得画面で60.0 FPSを確認。SELECT＋STARTメニューから終了し、SimpleMenuへ復帰。
4. 設定でSimpleQuestとSimpleQuest2を切り替え、両方のレイアウトを実機で取得。再起動・ゲームからの復帰後も選択と位置が保持される。
5. 日本語ROM名の漢字が欠けることを再現後、フォールバックにより「忍者龍剣伝」「星のカービィ」「魔界村」等を表示できることを確認。
6. SELECTのエミュ選択からPicoArch FCEUmmを選び、日本語ファイル名の魔界村を起動。正常な色のゲーム・メニュー表示、SELECT＋STARTから終了してSimpleMenuへ戻ることを確認。試験後はこのゲームのSimpleMenu側の選択をDefaultへ復元。
7. START → Session: quitで同じplumOS FEプロセスのAppsへ戻り、SimpleMenuの名前も消えないことを確認。最終版は詳細ログOFFの状態でも起動・終了を確認。
8. 再インストール時に既存のlast_state.savを保持することを確認。実機上の元テーマファイルとruntime、計125ファイルをSHA-256で照合。

これはSimpleMenu統合の表示・操作・起動・復帰の検証であり、全26機種をあらためて性能合格にしたという意味ではない。元テーマに素材がない機種はSimpleMenu標準の機種名表示へフォールバックする。ROMサムネイルがない場合は原版テーマの空の画像領域となる。

確認画像・ビルドログ・転送ログはGit管理外の`output/rg280v-simplemenu/`へ保存。SD2はread-onlyを維持。SDカードイメージは作成していない。

## 再現手順

```sh
scripts/build-rg280v-simplemenu.sh
python3 scripts/fetch-rg280v-simplequest.py
python3 scripts/install-rg280v-simplemenu.py
```

ビルドは既存の`plumos-jz47xx-build:bookworm`コンテナとMIPS SDKを使う。導入時は実機のSimpleMenuを終了し、ADBサーバー5041・`10.1.1.2:5555`へ接続する。インストーラはその時点の実機の有効な機種・コアから設定を生成する。初回のみHOMEをseedから作成し、再実行では既存のテーマ選択やお気に入り等を上書きしない。テーマデータを公開イメージへ埋め込む処理は追加していない。
