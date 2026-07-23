# うめンち ブランドサイト（umench-site）

うめンち（住宅系YouTube）のブランドLP。Fortress UI Kit（作戦司令室×機密ファイル世界観）を流用した単一HTML。

## ファイル

- `index.html` … サイト本体（外部依存は Google Fonts と YouTube サムネイル CDN のみ）
- `assets/` … 立ち絵画像（ume-commander.png=ヒーロー / mugi.png=脅威カード / ume-pointing.png=CTA）
  - 元素材: `~/Movies/うめンち物語用_立ち絵素材/`（透過トリム＋リサイズ済みを配置）

## ローカルプレビュー

```bash
cd ~/Documents/Claude/umench-site
python3 -m http.server 8951
# → http://localhost:8951
```

## リンク（すべて反映済み）

- YouTube: `https://www.youtube.com/@Umes-House`
- X: `https://x.com/UMEs_House`
- note: `https://note.com/umentch`

## GitHub Pages デプロイ手順

```bash
cd ~/Documents/Claude/umench-site
git init && git add . && git commit -m "うめンちブランドサイト初版"
gh repo create umench-site --public --source=. --push
gh api repos/{owner}/umench-site/pages -X POST -f "source[branch]=main" -f "source[path]=/"
# → https://<username>.github.io/umench-site/
```

（リポジトリ名・公開設定は好みに応じて変更。独自ドメインを使う場合は Pages 設定で CNAME を追加）

## セクション構成

ナビ / ヒーロー（CLASSIFIED・タイプライター名乗り・レーダー）/ 要塞スペック / 機密ファイルアーカイブ（コンテンツの型4種）/ 要塞化ステータス（ゲージ）/ 脅威レポート（むぎ・大型昆虫・変動金利）/ 名言 / 作戦ログ / 通信チャネル / CTA / フッター

## 一次資料

- デザイン原本: `~/Documents/Claude/umench-fortress-ui-kit.html`
- 世界観・文言: Obsidian `Projects/うめンち/ブランドガイド.md` / `要塞スペック.md`
- 絵文字不使用（ブランドNG遵守）
