# RG280V FBNeoのFE候補とROMセット確認（2026-11-16）

ユーザーがFBNeoのRA経路の廃止を指定した。PicoArchで `airduelm72.zip` を起動すると停止したままになり、実機の `Logs/picoarch/fbneo.log` には `ad-c-h0-c.ic40`（CRC `6467ed0f`）と `ad-c-l0-c.ic37`（CRC `b90c4ffd`）が必須と記録されていた。Mac上の同ZIPには両ファイルがなく、同じCRCのデータも含まれていない。実機とMac上のZIPのSHA-256は `9125b7d783a78ab1c2b6994219afbe0fac3d65cbe92248245a0d0ca9ed5245ed` で一致した。このROMセットは現在のFBNeoコアに合わない。

FEの候補と既定を `picoarch:fbneo` のみに変更し、設定更新用のマージ処理にもFBNeoを追加した。実機へ反映した設定のSHA-256は `cbf2a5a8cc4be502e9029f878a2cba10fa314d48e468442a3021bbb740141934`。マージ前後で変化した機種はFBNeoのみ。RA実行ファイル、ROM、SD2の内容は変更していない。SD2は引き続きVFATの読み取り専用マウント。

固定済みFBNeoソースの `FinalBurn Neo (ClrMame Pro XML, Arcade only).dat` と、手元の17本のZIP内CRCを照合した。`airduelm72`、`imgfight`、`kungfum`、`loht`、`nspirit`、`vigilantbl` は必須ファイルの不足が見つかった。`dbreedm72` はZIP内の必須CRCに欠落がないが親セットを参照するため、単体起動可否は未判定。親セットを持たない残り10本と `bchopper.zip` はZIP内の必須CRCに欠落がなかった。ただしCRC一致はゲーム動作の確認ではない。

次の確認には `bchopper.zip` を使う。このZIPの必須23ファイルはすべてCRC一致し、Macと実機のSHA-256は `df7478ae444ca2aa931afe788c0a36dfebeeb8f385db60f20a5699b25f14a1e8` で一致した。停止していたPicoArchプロセスはTERMに応答しなかったため終了させ、FEを再起動した。FEプロセス稼働を確認済み。更新後のPicoArch FBNeoによる映像・音・操作・FPS・メニュー終了後のFE復帰は実機で未確認。
