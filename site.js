/* Restaurant Spitz – kleines Skript. Die Seite funktioniert auch ohne:
   Menü-Overlay, Punkte und Autoplay der Karussells, Datumsfelder im Formular. */
(function(){
  var html=document.documentElement;

  // Menü
  var knopf=document.querySelector('.menueknopf'), menue=document.getElementById('menue');
  function zu(){html.classList.remove('menue-offen');if(knopf)knopf.setAttribute('aria-expanded','false')}
  if(knopf&&menue){
    knopf.addEventListener('click',function(){
      var offen=html.classList.toggle('menue-offen');
      knopf.setAttribute('aria-expanded',offen?'true':'false');
    });
    menue.addEventListener('click',function(e){if(e.target.closest('a'))zu()});
    document.addEventListener('keydown',function(e){if(e.key==='Escape')zu()});
  }

  // Kopfzeile: Logo beim Scrollen verkleinern
  function scroll(){html.classList.toggle('schmal',window.scrollY>window.innerHeight*.5)}
  window.addEventListener('scroll',scroll,{passive:true});scroll();

  // Karussells
  var still=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.karussell').forEach(function(k){
    var spur=k.querySelector('.spur'), bilder=spur.children, n=bilder.length;
    if(n<2)return;
    var punkte=document.createElement('div');punkte.className='punkte';
    var knoepfe=[];
    for(var i=0;i<n;i++){(function(i){
      var b=document.createElement('button');b.type='button';
      b.setAttribute('aria-label',(html.lang==='en'?'Image ':'Bild ')+(i+1)+' / '+n);
      b.addEventListener('click',function(){gehe(i);stopp()});
      punkte.appendChild(b);knoepfe.push(b);
    })(i)}
    k.appendChild(punkte);
    function aktuell(){return Math.round(spur.scrollLeft/spur.clientWidth)}
    function markieren(){var a=aktuell();knoepfe.forEach(function(b,i){b.setAttribute('aria-current',i===a?'true':'false')})}
    function gehe(i){spur.scrollTo({left:i*spur.clientWidth,behavior:still?'auto':'smooth'})}
    spur.addEventListener('scroll',function(){window.requestAnimationFrame(markieren)},{passive:true});
    markieren();
    var takt=null;
    function stopp(){if(takt){clearInterval(takt);takt=null}}
    if(k.hasAttribute('data-auto')&&!still){
      takt=setInterval(function(){if(!document.hidden)gehe((aktuell()+1)%n)},5000);
      spur.addEventListener('pointerdown',stopp);spur.addEventListener('wheel',stopp,{passive:true});
    }
  });

  // Anfrageformular: Datumsgrenzen, ausgeschriebenes Datum, Offerte-Pflichtfelder
  function iso(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)}
  var heute=new Date();
  ['f-datum','f-datum2','f-datum3'].forEach(function(id){
    var feld=document.getElementById(id), text=document.getElementById(id+'-text');
    if(!feld||!text)return;
    feld.min=iso(heute);feld.max=(heute.getFullYear()+2)+'-12-31';
    function schreiben(){var t=feld.value.split('-');
      text.value=t.length===3?new Date(+t[0],t[1]-1,+t[2]).toLocaleDateString('de-CH',{weekday:'long',day:'numeric',month:'long',year:'numeric'}):''}
    feld.addEventListener('change',schreiben);feld.addEventListener('input',schreiben);schreiben();
  });
  var offerte=document.getElementById('f-offerte');
  if(offerte){
    var pflicht=['f-firma','f-strasse','f-plz','f-ort'].map(function(id){return document.getElementById(id)});
    function umschalten(){pflicht.forEach(function(f){if(f)f.required=offerte.checked})}
    offerte.addEventListener('change',umschalten);umschalten();
  }
})();
