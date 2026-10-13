
(function(){
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#57ffdc';

  function waves(canvas, opts){
    var ctx = canvas.getContext('2d'); if(!ctx) return;
    var w, h, dpr;
    function size(){
      dpr = Math.min(window.devicePixelRatio||1, 2);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = w*dpr; canvas.height = h*dpr;
      ctx.setTransform(dpr,0,0,dpr,0,0);
    }
    function draw(t){
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
    if(reduce) return;
    function loop(t){ if(visible){ last = t + (opts.t0||0); draw(last); } requestAnimationFrame(loop); }
    requestAnimationFrame(loop);
  }
  var c1 = document.getElementById('waves'), c2 = document.getElementById('waves2');
  if(c1) waves(c1, {lines:46, base:0.62, spread:0.55, t0:0});
  if(c2) waves(c2, {lines:36, base:0.55, spread:0.7, t0:40000});

  // lightbox
  var lb = document.getElementById('lb'), img = document.getElementById('lbImg'), cap = document.getElementById('lbCap');
  document.addEventListener('click', function(e){
    var t = e.target.closest && e.target.closest('img.zoom');
    if(!t || !lb.showModal) return;
    img.src = t.currentSrc || t.src; img.alt = t.alt; cap.textContent = t.alt;
    lb.showModal();
  });
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
})();
