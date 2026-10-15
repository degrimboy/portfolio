
(function(){
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;
  function getPref(k){ try { return localStorage.getItem(k); } catch(e){ return null; } }
  function setPref(k,v){ try { localStorage.setItem(k,v); } catch(e){} }
  // Player settings: motion follows the visitor's system setting unless they choose otherwise
  var motionPref = getPref('sts-motion');
  var motionOn = motionPref ? motionPref === 'on' : !reduce;
  root.classList.toggle('no-motion', !motionOn);
  if(getPref('sts-size') === 'large') root.classList.add('text-large');
  function motionAllowed(){ return !root.classList.contains('no-motion'); }
  var accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#57ffdc';
  var hexMotif = document.documentElement.getAttribute('data-motif') === 'hex' || !!document.querySelector('.cardhero');

  function waves(canvas, opts){
    var ctx = canvas.getContext('2d'); if(!ctx) return;
    var w, h, dpr;
    function size(){
      dpr = Math.min(window.devicePixelRatio||1, 2);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = w*dpr; canvas.height = h*dpr;
      ctx.setTransform(dpr,0,0,dpr,0,0);
    }
    var lineColor = getComputedStyle(canvas).getPropertyValue('--wave').trim() || accent;
    function drawHex(t){
      // flat-top hexagons, like the tiles on a cafe table, with light drifting slowly across them
      ctx.clearRect(0,0,w,h);
      ctx.strokeStyle = lineColor; ctx.lineWidth = 1;
      var r = Math.max(26, Math.min(44, w/30)), hw = r*1.5, hh = Math.sqrt(3)*r;
      for(var col=-1; col*hw < w + r; col++){
        for(var row=-1; row*hh < h + hh; row++){
          var cx = col*hw, cy = row*hh + (col%2 ? hh/2 : 0);
          var fade = Math.min(1, Math.max(0, (cx/w)*0.9 + (cy/h)*0.6 - 0.35));
          var glow = 0.55 + 0.45*Math.sin(t*0.0004 + cx*0.006 - cy*0.004);
          var a = fade * glow * opts.hexAlpha;
          if(a < 0.01) continue;
          ctx.globalAlpha = a;
          ctx.beginPath();
          for(var k=0;k<6;k++){ var ang = Math.PI/3*k; var x = cx + r*Math.cos(ang), y = cy + r*Math.sin(ang); if(k) ctx.lineTo(x,y); else ctx.moveTo(x,y); }
          ctx.closePath(); ctx.stroke();
        }
      }
      ctx.globalAlpha = 1;
    }
    function draw(t){
      if(hexMotif) return drawHex(t);
      ctx.clearRect(0,0,w,h);
      ctx.strokeStyle = accent; ctx.lineWidth = 1;
      var n = opts.lines;
      for(var i=0;i<n;i++){
        var k = i/(n-1);
        ctx.globalAlpha = 0.06 + 0.22*Math.sin(Math.PI*k);
        ctx.beginPath();
        for(var x=0;x<=w+8;x+=8){
          var u = x/w;
          var y = h*opts.base
            + Math.sin(u*3.1 + t*0.00018 + k*1.9)*h*0.14
            + Math.sin(u*7.3 - t*0.00011 + k*3.4)*h*0.05*(1-k)
            + (k-0.5)*h*opts.spread*(0.35+u);
          if(x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }
    size(); draw(opts.t0||0);
    window.addEventListener('resize', function(){ size(); draw(last); });
    var last = opts.t0||0, visible = true;
    if('IntersectionObserver' in window){
      new IntersectionObserver(function(e){ visible = e[0].isIntersecting; }).observe(canvas);
    }
    var runUntil = performance.now() + 5000;
    var zone = canvas.parentElement;
    function wake(){ runUntil = performance.now() + 5000; }
    if(zone){ zone.addEventListener('pointerenter', wake); zone.addEventListener('focusin', wake); }
    // On phones the hex pattern is drawn once and kept still: animating it costs too much on slow processors
    if(hexMotif && window.innerWidth < 900) return;
    function loop(t){ if(visible && motionAllowed() && t < runUntil){ last = t + (opts.t0||0); draw(last); } requestAnimationFrame(loop); }
    requestAnimationFrame(loop);
  }
  var c1 = document.getElementById('waves'), c2 = document.getElementById('waves2');
  if(c1) waves(c1, {lines:46, base:0.62, spread:0.55, t0:0, hexAlpha:(innerWidth<700?0.16:0.26)});
  if(c2) waves(c2, {lines:36, base:0.55, spread:0.7, t0:40000, hexAlpha:0.22});

  // lightbox
  var lb = document.getElementById('lb'), img = document.getElementById('lbImg'), cap = document.getElementById('lbCap');
  document.addEventListener('click', function(e){
    var b = e.target.closest && e.target.closest('.zoom-btn');
    if(!b || !lb.showModal) return;
    var t = b.querySelector('img');
    img.src = t.currentSrc || t.src; img.alt = t.alt; cap.textContent = t.alt;
    lastZoom = b;
    lb.showModal();
  });
  var lastZoom = null;
  lb.addEventListener('close', function(){ if(lastZoom) lastZoom.focus(); });
  document.getElementById('lbClose').addEventListener('click', function(){ lb.close(); });
  lb.addEventListener('click', function(e){ if(e.target === lb) lb.close(); });

  // YouTube: swap the thumbnail for the player on click
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a.yt');
    if(!a) return;
    e.preventDefault();
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + a.dataset.yt + '?autoplay=1&rel=0';
    f.title = a.dataset.title || 'YouTube video';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.allowFullscreen = true;
    f.setAttribute('loading','lazy');
    a.replaceWith(f);
    f.focus();
  });

  // Player settings panel
  var btn = document.getElementById('settingsBtn'), panel = document.getElementById('settings');
  if(btn && panel){
    var sw = document.getElementById('optMotion');
    var sizeBtns = panel.querySelectorAll('[data-size]');
    function sync(){
      sw.setAttribute('aria-checked', motionAllowed() ? 'true' : 'false');
      var large = root.classList.contains('text-large');
      sizeBtns.forEach(function(b){ b.setAttribute('aria-pressed', (b.dataset.size === 'large') === large ? 'true' : 'false'); });
    }
    function close(){ panel.hidden = true; btn.setAttribute('aria-expanded','false'); }
    btn.addEventListener('click', function(){ var open = panel.hidden; panel.hidden = !open; btn.setAttribute('aria-expanded', open ? 'true' : 'false'); if(open) sw.focus(); });
    sw.addEventListener('click', function(){ var on = !motionAllowed(); root.classList.toggle('no-motion', !on); setPref('sts-motion', on ? 'on' : 'off'); sync(); });
    sizeBtns.forEach(function(b){ b.addEventListener('click', function(){ var large = b.dataset.size === 'large'; root.classList.toggle('text-large', large); setPref('sts-size', large ? 'large' : 'std'); sync(); }); });
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape' && !panel.hidden){ close(); btn.focus(); } });
    document.addEventListener('click', function(e){ if(!panel.hidden && !panel.contains(e.target) && !btn.contains(e.target)) close(); });
    sync();
    document.querySelectorAll('[data-open-settings]').forEach(function(a){ a.addEventListener('click', function(e){ e.preventDefault(); window.scrollTo({top:0, behavior: motionAllowed() ? 'smooth' : 'auto'}); panel.hidden = false; btn.setAttribute('aria-expanded','true'); setTimeout(function(){ sw.focus(); }, motionAllowed() ? 400 : 0); }); });
  }

  // Copy email
  document.querySelectorAll('[data-copy]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var text = btn.getAttribute('data-copy'), label = btn.textContent;
      function done(msg){ btn.textContent = msg; setTimeout(function(){ btn.textContent = label; }, 2000); }
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(text).then(function(){ done('Copied'); }, function(){ selectEmail(); done('Press Ctrl+C to copy'); });
      } else { selectEmail(); done('Press Ctrl+C to copy'); }
      function selectEmail(){ var el = btn.parentElement.querySelector('.email'); var r = document.createRange(); r.selectNodeContents(el); var sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); }
    });
  });
})();
