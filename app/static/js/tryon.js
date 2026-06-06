const MODEL_URL='https://justadudewhohacks.github.io/face-api.js/models';
let modelsLoaded=false, isDragging=false, startX, startY;
let baseLeft=25, baseTop=35, baseWidth=50, baseRotate=0;
let originalFrameSrc=''; // store original frame src for re-processing

// ---- Smart Background Removal (any color) ----
function getPixel(d, x, y, w) {
  const i = (y * w + x) * 4;
  return { r: d[i], g: d[i+1], b: d[i+2] };
}

function removeWhiteBg(imgSrc, callback) {
  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = function() {
    const c = document.createElement('canvas');
    c.width = img.naturalWidth;
    c.height = img.naturalHeight;
    const ctx = c.getContext('2d');
    ctx.drawImage(img, 0, 0);
    const id = ctx.getImageData(0, 0, c.width, c.height);
    const d = id.data;
    const w = c.width, h = c.height;

    // Sample background color from 12 points around edges
    const samples = [
      getPixel(d,2,2,w), getPixel(d,w-3,2,w),
      getPixel(d,2,h-3,w), getPixel(d,w-3,h-3,w),
      getPixel(d,Math.floor(w/2),2,w), getPixel(d,Math.floor(w/2),h-3,w),
      getPixel(d,2,Math.floor(h/2),w), getPixel(d,w-3,Math.floor(h/2),w),
      getPixel(d,10,10,w), getPixel(d,w-11,10,w),
      getPixel(d,10,h-11,w), getPixel(d,w-11,h-11,w),
    ];
    const bg = {
      r: Math.round(samples.reduce((s,p)=>s+p.r,0)/samples.length),
      g: Math.round(samples.reduce((s,p)=>s+p.g,0)/samples.length),
      b: Math.round(samples.reduce((s,p)=>s+p.b,0)/samples.length)
    };

    const threshold = 65;
    for (let i = 0; i < d.length; i += 4) {
      const dist = Math.sqrt(
        Math.pow(d[i]-bg.r,2) + Math.pow(d[i+1]-bg.g,2) + Math.pow(d[i+2]-bg.b,2)
      );
      if (dist < threshold) {
        d[i+3] = Math.min(d[i+3], Math.round((dist/threshold)*255));
      }
    }
    ctx.putImageData(id, 0, 0);
    callback(c.toDataURL('image/png'));
  };
  img.onerror = function() { callback(imgSrc); };
  img.src = imgSrc;
}

// ---- Face Detection Models ----
async function loadFaceModels(){
  if(modelsLoaded) return;
  await Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
    faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODEL_URL)
  ]);
  modelsLoaded=true;
}

// ---- Detect Face & Auto-Fit Frame ----
async function detectAndFit(imgEl){
  const ld=document.getElementById('tryOnLoading');
  const bd=document.getElementById('autoFitBadge');
  if(ld) ld.style.display='flex';
  if(bd) bd.style.display='none';
  try{
    await loadFaceModels();
    const det=await faceapi.detectSingleFace(imgEl,new faceapi.TinyFaceDetectorOptions({inputSize:416,scoreThreshold:0.3})).withFaceLandmarks(true);
    if(!det){if(bd){bd.textContent='⚠ No face found';bd.className='tryon-badge warn';bd.style.display='block';}if(ld)ld.style.display='none';return;}

    const box=det.detection.box;
    const le=det.landmarks.getLeftEye(), re=det.landmarks.getRightEye();
    const lc=avg(le), rc=avg(re);
    const eyeMid={x:(lc.x+rc.x)/2, y:(lc.y+rc.y)/2};
    const angle=Math.atan2(rc.y-lc.y,rc.x-lc.x)*(180/Math.PI);

    const container=document.getElementById('tryOnCanvas');
    const t=coverTransform(imgEl,container);
    const cW=container.clientWidth, cH=container.clientHeight;

    const faceWidthDisp=box.width*t.scale;
    const fw=faceWidthDisp*1.05;
    const dm=toDisplay(eyeMid.x,eyeMid.y,t);

    const frameImg=document.getElementById('tryOnFrame');
    const frameAR=frameImg.naturalWidth/frameImg.naturalHeight||3;
    const fh=fw/frameAR;

    baseWidth=(fw/cW)*100;
    baseLeft=((dm.x-fw/2)/cW)*100;
    baseTop=((dm.y-fh*0.42)/cH)*100;
    baseRotate=angle;

    applyBase(); resetSliders();
    if(bd){bd.textContent='✓ Auto-fitted!';bd.className='tryon-badge ok';bd.style.display='block';}
  }catch(e){
    console.error('Face detection error',e);
    if(bd){bd.textContent='⚠ Adjust manually';bd.className='tryon-badge warn';bd.style.display='block';}
  }
  if(ld) ld.style.display='none';
}

function avg(pts){return{x:pts.reduce((s,p)=>s+p.x,0)/pts.length,y:pts.reduce((s,p)=>s+p.y,0)/pts.length};}
function coverTransform(img,box){
  const ir=img.naturalWidth/img.naturalHeight,cr=box.clientWidth/box.clientHeight;
  let dw,dh,ox,oy;
  if(ir>cr){dh=box.clientHeight;dw=dh*ir;ox=(box.clientWidth-dw)/2;oy=0;}
  else{dw=box.clientWidth;dh=dw/ir;ox=0;oy=(box.clientHeight-dh)/2;}
  return{scale:dw/img.naturalWidth,offsetX:ox,offsetY:oy};
}
function toDisplay(x,y,t){return{x:x*t.scale+t.offsetX,y:y*t.scale+t.offsetY};}

function applyBase(){
  const f=document.getElementById('tryOnFrame');
  if(!f)return;
  f.style.width=baseWidth+'%';
  f.style.left=baseLeft+'%';
  f.style.top=baseTop+'%';
  f.style.transform='rotate('+baseRotate+'deg)';
}

// ---- Open / Close Modal ----
function openTryOn(){
  const m=document.getElementById('tryOnModal');
  if(!m)return;
  m.classList.add('open');
  document.body.style.overflow='hidden';

  // Process frame image to remove white background (one-time)
  const frameEl=document.getElementById('tryOnFrame');
  if(frameEl && !frameEl.dataset.processed){
    originalFrameSrc = frameEl.src;
    removeWhiteBg(originalFrameSrc, function(transparentSrc){
      frameEl.src = transparentSrc;
      frameEl.dataset.processed = 'true';
      // Now detect face
      startDetection();
    });
  } else {
    startDetection();
  }
}

function startDetection(){
  const saved=getSavedSelfie();
  if(saved){loadSavedSelfie(saved);}
  else{
    const img=document.getElementById('tryOnFaceBg');
    if(img.complete&&img.naturalWidth)detectAndFit(img);else img.onload=()=>detectAndFit(img);
  }
}

function closeTryOn(){const m=document.getElementById('tryOnModal');if(m){m.classList.remove('open');document.body.style.overflow='';}}

// ---- localStorage Selfie ----
function saveSelfie(d){try{localStorage.setItem('ayan_tryon_selfie',d);}catch(e){}}
function getSavedSelfie(){return localStorage.getItem('ayan_tryon_selfie');}

function loadSavedSelfie(dataUrl){
  const bg=document.getElementById('tryOnFaceBg');
  bg.removeAttribute('crossorigin');
  bg.src=dataUrl;
  const sec=document.getElementById('savedPhotoSection'),thumb=document.getElementById('savedPhotoImg');
  if(sec)sec.style.display='block';
  if(thumb)thumb.src=dataUrl;
  document.querySelectorAll('.model-thumb').forEach(t=>t.classList.remove('active'));
  const st=document.getElementById('savedPhotoThumb');
  if(st)st.classList.add('active');
  bg.onload=()=>detectAndFit(bg);
}

function handleSelfieUpload(event){
  const file=event.target.files[0];if(!file)return;
  const reader=new FileReader();
  reader.onload=function(e){saveSelfie(e.target.result);loadSavedSelfie(e.target.result);};
  reader.readAsDataURL(file);
}
function changePhoto(){document.getElementById('selfieUpload').click();}

function switchModel(el){
  document.querySelectorAll('.model-thumb').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  const bg=document.getElementById('tryOnFaceBg');
  bg.setAttribute('crossorigin','anonymous');
  bg.src=el.getAttribute('data-img');
  bg.onload=()=>detectAndFit(bg);
}

// ---- Sliders ----
function resetSliders(){
  document.getElementById('scaleSlider').value=100;
  document.getElementById('xSlider').value=0;
  document.getElementById('ySlider').value=0;
  document.getElementById('rotateSlider').value=0;
  updateSliderLabels();
}
function updateSliderLabels(){
  document.getElementById('scaleVal').innerText=document.getElementById('scaleSlider').value+'%';
  document.getElementById('xVal').innerText=document.getElementById('xSlider').value+'px';
  document.getElementById('yVal').innerText=document.getElementById('ySlider').value+'px';
  document.getElementById('rotateVal').innerText=document.getElementById('rotateSlider').value+'°';
}
function updateFrameTransform(){
  const s=document.getElementById('scaleSlider').value/100;
  const x=+document.getElementById('xSlider').value;
  const y=+document.getElementById('ySlider').value;
  const r=+document.getElementById('rotateSlider').value;
  updateSliderLabels();
  const f=document.getElementById('tryOnFrame');
  if(f){f.style.width=baseWidth+'%';f.style.left=baseLeft+'%';f.style.top=baseTop+'%';
    f.style.transform='translate('+x+'px,'+y+'px) scale('+s+') rotate('+(baseRotate+r)+'deg)';}
}
function resetControls(){
  const img=document.getElementById('tryOnFaceBg');
  if(img.complete&&img.naturalWidth)detectAndFit(img);
  else{baseLeft=25;baseTop=35;baseWidth=50;baseRotate=0;applyBase();resetSliders();}
}
function toggleBlendMode(cb){
  const f=document.getElementById('tryOnFrame');
  if(!f) return;
  if(cb.checked && originalFrameSrc){
    // Re-process to remove background
    removeWhiteBg(originalFrameSrc, function(src){ f.src=src; f.dataset.processed='true'; });
  } else if(originalFrameSrc){
    // Show original with background
    f.src=originalFrameSrc; f.dataset.processed='';
  }
}

// ---- Drag ----
function dragStart(e){
  isDragging=true;
  const cx=e.touches?e.touches[0].clientX:e.clientX,cy=e.touches?e.touches[0].clientY:e.clientY;
  startX=cx-(+document.getElementById('xSlider').value||0);
  startY=cy-(+document.getElementById('ySlider').value||0);
  e.preventDefault();
}
function dragMove(e){
  if(!isDragging)return;
  const cx=e.touches?e.touches[0].clientX:e.clientX,cy=e.touches?e.touches[0].clientY:e.clientY;
  document.getElementById('xSlider').value=Math.max(-150,Math.min(150,cx-startX));
  document.getElementById('ySlider').value=Math.max(-150,Math.min(150,cy-startY));
  updateFrameTransform();
  if(e.cancelable)e.preventDefault();
}
function dragEnd(){isDragging=false;}

// ---- Init ----
document.addEventListener('DOMContentLoaded',()=>{
  const openBtn=document.getElementById('openTryOnBtn');
  if(openBtn)openBtn.addEventListener('click',openTryOn);
  const frameEl=document.getElementById('tryOnFrame');
  if(frameEl){
    originalFrameSrc = frameEl.src;
    frameEl.addEventListener('mousedown',dragStart);
    window.addEventListener('mousemove',dragMove);
    window.addEventListener('mouseup',dragEnd);
    frameEl.addEventListener('touchstart',dragStart,{passive:false});
    window.addEventListener('touchmove',dragMove,{passive:false});
    window.addEventListener('touchend',dragEnd);
  }
  const saved=getSavedSelfie();
  if(saved){
    const sec=document.getElementById('savedPhotoSection'),thumb=document.getElementById('savedPhotoImg');
    if(sec)sec.style.display='block';
    if(thumb)thumb.src=saved;
  }
});
