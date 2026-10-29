/* ==========================================================================
   LIVESTREAM: race clock + sponsor banner
   ----------------------------------------------------------------------------
   STREAM.youtubeId : the 11-character ID of the scheduled YouTube stream
                      (the part after watch?v= in its link). Leave '' to show
                      the "starts on race day" panel instead of a player.
   STREAM.delaySeconds : how far YouTube runs behind real life. The clock is
                      held back by this much so it matches what viewers see.
                      Measure it in the test stream; ~3-5 with Ultra low latency.

   Preview tricks (no code change needed):
     <page>?v=VIDEO_ID       try any YouTube video or stream in the player
     <page>?t=10:57          run the clock as if it's 10:57 AM on race day

   Used by index.html and race-day.html (both load this file), so set
   youtubeId once here and the stream shows on both pages.
   ========================================================================== */
var STREAM = {
  youtubeId: '',
  delaySeconds: 0
};

/* Generated from tools/sponsors.json by tools/build_sponsors.py - edit there, not here */
var LIVE_SPONSORS = [
  /* LIVE_SPONSORS:START */
    {"slug": "ultimate-direction", "name": "Ultimate Direction", "href": "https://ultimatedirection.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "horse-and-dragon", "name": "Horse & Dragon Brewing", "href": "https://www.horseanddragonbrewing.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "salty-britches", "name": "Salty Britches", "href": "https://getsaltybritches.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "red-silo-coffee", "name": "Red Silo Coffee Roasters", "href": "https://www.redsilocoffeeroasters.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "quinn-snacks", "name": "Quinn Snacks", "href": "https://www.quinnsnacks.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "plain-am", "name": "Plain AM", "href": "https://www.plain-am.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "bobs-pickle-pops", "name": "Bob's Pickle Pops", "href": "https://bobspicklepops.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "territory-run", "name": "Territory Run Co.", "href": "https://territoryrun.co/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "colorado-compass", "name": "Colorado Compass", "href": "https://colorado-compass.beehiiv.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "natural-groceries", "name": "Natural Grocers", "href": "https://www.naturalgrocers.com/store/golden?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "fastsigns", "name": "FASTSIGNS Lakewood", "href": "https://www.fastsigns.com/lakewood-co/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "eldorado", "name": "Eldorado Natural Spring Water", "href": "https://www.eldoradosprings.com/?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
    {"slug": "fedex-office-golden", "name": "FedEx Office Golden", "href": "https://local.fedex.com/en-us/co/golden/office-0470?utm_source=bearcreekbackyardultra&utm_medium=livestream&utm_campaign=11th_hour_backyard_ultra&utm_content=stream_banner", "dark": false},
  /* LIVE_SPONSORS:END */
];

(function(){
  if (!document.getElementById('live-video')) return;
  var RACE_START = Date.UTC(2026, 9, 31, 14, 0, 0); // Sat Oct 31, 8:00 AM Mountain (MDT, UTC-6)
  var LOOP_MS = 3600000;
  var MAX_LOOPS = 11;
  var RACE_END = RACE_START + MAX_LOOPS * LOOP_MS;   // 7:00 PM: last loop must be done
  var CORRAL_CALL_S = 180;                           // 3-minute whistle before each start
  var ROTATE_MS = 20000;

  var params = new URLSearchParams(location.search);
  var videoId = (params.get('v') || STREAM.youtubeId || '').trim();
  var delayMs = (Number(STREAM.delaySeconds) || 0) * 1000;

  // Clock source: the website server's time (one quick request), not the viewer's
  // device clock, which can be off by minutes.
  var skew = 0;
  try {
    fetch(location.pathname + '?clock=' + Date.now(), {method: 'HEAD', cache: 'no-store'}).then(function(r){
      var d = Date.parse(r.headers.get('Date'));
      if (!isNaN(d)) skew = d + 500 - Date.now();
    }).catch(function(){});
  } catch (e) {}

  // ?t=HH:MM[:SS] preview: pretend it's that time on race day, then run forward
  var simShift = 0;
  var tm = (params.get('t') || '').match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/);
  if (tm) {
    var simAt = Date.UTC(2026, 9, 31, Number(tm[1]) + 6, Number(tm[2]), Number(tm[3] || 0));
    simShift = simAt - Date.now();
  }
  function now(){ return Date.now() + (simShift || skew) - delayMs; }

  var $ = function(id){ return document.getElementById(id); };
  var elLoop = $('lb-loop'), elNext = $('lb-next'), elNextLabel = $('lb-next-label'),
      elMain = $('lb-main'), elElapsed = $('lb-elapsed'), elStatus = $('live-status'),
      elKicker = $('live-kicker'), elLede = $('live-lede');

  function pad(n){ return n < 10 ? '0' + n : '' + n; }
  function hms(ms){
    var s = Math.max(0, Math.floor(ms / 1000));
    return Math.floor(s / 3600) + ':' + pad(Math.floor(s / 60) % 60) + ':' + pad(s % 60);
  }
  function countdown(ms){
    var s = Math.max(0, Math.ceil(ms / 1000));
    if (s >= 86400) return Math.floor(s / 86400) + 'd ' + Math.floor(s / 3600) % 24 + 'h';
    if (s >= 3600) return hms(s * 1000);
    return pad(Math.floor(s / 60)) + ':' + pad(s % 60);
  }
  function loopHtml(n){ return n + ' <span class="of">/ ' + MAX_LOOPS + '</span>'; }

  var lastPhase = '';
  function setPhase(phase){
    if (phase === lastPhase) return;
    lastPhase = phase;
    if (phase === 'before') {
      elStatus.textContent = 'Livestream · Saturday, October 31';
    } else if (phase === 'during') {
      elStatus.textContent = videoId ? 'Live now from Bear Creek Lake Park' : 'Race in progress';
      elLede.textContent = 'Follow every loop from the start corral at Pelican Point. Runners head out at the top of every hour.';
    } else {
      elStatus.textContent = 'Race complete';
      elLede.textContent = 'That’s a wrap. Thanks for cheering every loop! The full stream replay is below.';
    }
    elKicker.classList.toggle('is-live', phase === 'during' && !!videoId);
  }

  function tick(){
    var t = now();
    var warn = false;
    if (t < RACE_START) {
      setPhase('before');
      elLoop.innerHTML = '&mdash;';
      var toGo = RACE_START - t;
      warn = toGo <= CORRAL_CALL_S * 1000;
      elNextLabel.textContent = warn ? 'Corral call · race starts in' : 'Race starts in';
      elNext.textContent = countdown(toGo);
      elElapsed.textContent = '0:00:00';
    } else if (t < RACE_END) {
      setPhase('during');
      var k = Math.floor((t - RACE_START) / LOOP_MS);          // 0..10
      elLoop.innerHTML = loopHtml(k + 1);
      if (k + 1 < MAX_LOOPS) {
        var next = RACE_START + (k + 1) * LOOP_MS - t;
        warn = next <= CORRAL_CALL_S * 1000;
        elNextLabel.textContent = (warn ? 'Corral call · loop ' : 'Loop ') + (k + 2) + ' starts in';
        elNext.textContent = countdown(next);
      } else {
        elNextLabel.textContent = 'Final loop · course closes in';
        elNext.textContent = countdown(RACE_END - t);
      }
      elElapsed.textContent = hms(t - RACE_START);
    } else {
      setPhase('after');
      elLoop.innerHTML = loopHtml(MAX_LOOPS);
      elNextLabel.textContent = 'Race complete';
      elNext.textContent = 'Finished';
      elElapsed.textContent = hms(RACE_END - RACE_START);
    }
    elMain.classList.toggle('warn', warn);
  }
  tick();
  setInterval(tick, 250);

  // ---- Player ----
  if (/^[A-Za-z0-9_-]{11}$/.test(videoId)) {
    var box = $('live-video');
    box.classList.remove('no-stream');
    box.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + videoId +
      '?autoplay=1&mute=1&playsinline=1&rel=0&modestbranding=1" title="11th Hour Backyard Ultra livestream"' +
      ' allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    if (window.mixpanel) mixpanel.track('Livestream Loaded', {video_id: videoId});
  } else {
    videoId = '';
  }

  // ---- Sponsor banner ----
  var link = $('lb-sponsor'), plate = $('lb-plate'), logo = $('lb-logo');
  var list = LIVE_SPONSORS.slice();
  if (!list.length) return;
  list.forEach(function(s){ var i = new Image(); i.src = 'images/sponsors/' + s.slug + '.png'; });
  var idx = Math.floor(Math.random() * list.length);   // spread first impressions across sponsors
  function show(s){
    logo.src = 'images/sponsors/' + s.slug + '.png';
    logo.alt = s.name;
    link.href = s.href || 'sponsors.html';
    link.setAttribute('aria-label', 'Sponsor: ' + s.name);
    link.dataset.sponsor = s.name;
    link.dataset.slug = s.slug;
    plate.classList.toggle('dark', !!s.dark);
  }
  show(list[idx]);
  setInterval(function(){
    if (document.hidden) return;
    idx = (idx + 1) % list.length;
    logo.classList.add('out');
    setTimeout(function(){ show(list[idx]); logo.classList.remove('out'); }, 450);
  }, ROTATE_MS);
  link.addEventListener('click', function(){
    if (window.mixpanel) {
      mixpanel.track('Sponsor Click', {sponsor: link.dataset.sponsor, slug: link.dataset.slug, via: 'livestream', page: location.pathname, destination: link.href}, {transport: 'sendBeacon'});
    }
  });
})();
