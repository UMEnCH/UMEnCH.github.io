/* うめンち サイト共通スクリプト
   役割:
     1. GA4（Googleアナリティクス4）の読み込み
     2. 外部リンク（アフィリエイト・YouTube・SNS）のクリック計測
     3. 物語ビューアなど、ページ側から任意イベントを送るための window.umTrack()

   ▼ 計測を始めるには、すぐ下の UM_GA_ID に GA4 の測定ID（G-から始まる文字列）を入れるだけ。
     空のままなら GA4 は一切読み込まれない（Cookie も発行されない）。 */

(function () {
  'use strict';

  // ===== 設定 =========================================================
  var UM_GA_ID = 'G-FSPMGP6FDV';
  // ====================================================================

  // ローカル（http://localhost… / file://）では送信しない。
  // 動作確認のクリックが本番のレポートに混ざらないようにするため、
  // コンソールへの出力だけ行う。
  var isLocal = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname)
             || location.protocol === 'file:';
  var enabled = /^G-[A-Z0-9]+$/i.test(UM_GA_ID) && !isLocal;

  // ---- GA4 の読み込み ----
  if (enabled) {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + UM_GA_ID;
    document.head.appendChild(s);

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', UM_GA_ID);
  }

  /** イベント送信。GA4未設定でもローカルではコンソールに出るので動作確認できる。 */
  function track(name, params) {
    params = params || {};
    if (isLocal) console.debug('[umTrack]', name, params);
    if (enabled && typeof window.gtag === 'function') window.gtag('event', name, params);
  }
  window.umTrack = track;

  // ---- リンク先の分類 ----
  // 収益に直結する導線（物販・チャンネル登録）を、その他の外部リンクと分けて数える
  function classify(url) {
    var h = '';
    try { h = new URL(url, location.href).hostname.replace(/^www\./, ''); } catch (e) { return null; }
    if (h === location.hostname || h === '') return null; // 内部リンクは対象外

    if (/(^|\.)(amazon\.co\.jp|amazon\.com)$/.test(h) || h === 'amzn.to' || h === 'amzn.asia') {
      return { event: 'affiliate_click', merchant: 'amazon' };
    }
    if (/rakuten/.test(h)) return { event: 'affiliate_click', merchant: 'rakuten' };
    if (/(yahoo|lohaco)/.test(h)) return { event: 'affiliate_click', merchant: 'yahoo' };
    if (/townlife/.test(h)) return { event: 'affiliate_click', merchant: 'townlife' };
    if (h === 'youtube.com' || h === 'youtu.be' || h === 'm.youtube.com') {
      return { event: 'youtube_click', merchant: '' };
    }
    if (h === 'x.com' || h === 'twitter.com') return { event: 'sns_click', merchant: 'x' };
    if (h === 'note.com') return { event: 'sns_click', merchant: 'note' };
    return { event: 'outbound_click', merchant: '' };
  }

  // YouTubeリンクの用途（登録／動画／チャンネル）を URL から判定
  function youtubeTarget(url) {
    if (/sub_confirmation=1/.test(url)) return 'subscribe';
    if (/(watch\?v=|youtu\.be\/|\/shorts\/)/.test(url)) return 'video';
    return 'channel';
  }

  // クリックされたリンクが「どこの何か」を、既存のHTML構造から自動で読み取る
  function context(a) {
    var ctx = { area: '', item: '', genre: '' };

    // 明示指定があればそれを優先（data-track="hero-cta" のように任意で付けられる）
    if (a.dataset && a.dataset.track) ctx.area = a.dataset.track;

    var product = a.closest('.product');
    if (product) {
      var h3 = product.querySelector('h3');
      if (h3) ctx.item = h3.textContent.trim();
      var sector = a.closest('.sector');
      var sh = sector && sector.querySelector('.sector-head h2');
      if (sh) ctx.genre = sh.textContent.trim();
      if (!ctx.area) ctx.area = 'arsenal-product';
    }

    if (!ctx.area) {
      var sec = a.closest('section[id]');
      if (sec) ctx.area = sec.id;
      else if (a.closest('nav')) ctx.area = 'nav';
      else if (a.closest('footer')) ctx.area = 'footer';
      else if (a.closest('.page-hero, .arsenal-hero, .hero')) ctx.area = 'hero';
    }
    return ctx;
  }

  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || typeof t.closest !== 'function') return;
    var a = t.closest('a[href]');
    if (!a) return;

    var href = a.getAttribute('href') || '';
    if (/^(#|mailto:|tel:|javascript:)/.test(href)) return;

    var kind = classify(href);
    if (!kind) return;

    var ctx = context(a);
    var params = {
      link_url: a.href,
      link_text: (a.textContent || '').trim().slice(0, 60),
      page_area: ctx.area,
      page_path: location.pathname + location.search
    };
    if (kind.merchant) params.merchant = kind.merchant;
    if (ctx.item) params.item_name = ctx.item;
    if (ctx.genre) params.item_genre = ctx.genre;
    if (kind.event === 'youtube_click') params.yt_target = youtubeTarget(a.href);

    track(kind.event, params);
  }, true);

  // ---- 物語ビューア: どの作品が開かれたかを記録 ----
  if (/story\.html$/.test(location.pathname)) {
    var id = new URLSearchParams(location.search).get('id');
    track('story_open', { story_id: id || '(index)' });
  }
})();
