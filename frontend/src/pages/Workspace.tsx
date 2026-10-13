import { useState, useRef, useEffect } from 'react';
import { Upload, Play, RotateCcw, CheckCircle2, CircleDashed, Circle, ZoomIn, X, SlidersHorizontal, Layers } from 'lucide-react';

const STAGES = [
  { id: 1,  label: 'Ingest & Label Parse',    real: true  },
  { id: 2,  label: 'Footprint Overlap',        real: true  },
  { id: 3,  label: 'CLAHE Enhancement',        real: true  },
  { id: 4,  label: 'GSD Normalization',        real: true  },
  { id: 5,  label: 'SIFT Extraction',          real: true  },
  { id: 6,  label: 'Candidate Matching',       real: true  },
  { id: 7,  label: 'RANSAC Verification',      real: true  },
  { id: 8,  label: 'Homography Fit',           real: true  },
  { id: 9,  label: 'Sub-Pixel Refinement',     real: false },
  { id: 10, label: 'Uncertainty Analysis',     real: false },
];

const PRODUCTS = [
  { key:'reg', label:'Registered Image',          src:'/api/outputs/registered_image.png',   status:'REAL',      sc:'text-green-400 border-green-500/50 bg-green-500/10',    cap:'OHRC warped onto LRO frame via RANSAC homography' },
  { key:'tie', label:'Matched Tie-Points',        src:'/api/outputs/matched_tiepoints.png',  status:'REAL',      sc:'text-green-400 border-green-500/50 bg-green-500/10',    cap:'Dim = candidates · Cyan circles = RANSAC inliers' },
  { key:'dem', label:'DEM / Terrain Product',     src:'/api/outputs/dem_product.png',        status:'SIMULATED', sc:'text-yellow-400 border-yellow-500/50 bg-yellow-500/10', cap:'OHRC intensity proxy – SPICE/LOLA planned' },
  { key:'fp',  label:'Footprints & Metadata',     src:'/api/outputs/footprints_metadata.png',status:'REAL',      sc:'text-green-400 border-green-500/50 bg-green-500/10',    cap:'OHRC ∩ LRO NAC geographic intersection' },
  { key:'unc', label:'Uncertainty / Validity Map',src:'/api/outputs/uncertainty_map.png',    status:'PARTIAL',   sc:'text-amber-400 border-amber-500/50 bg-amber-500/10',    cap:'Gaussian confidence field · red=high uncertainty' },
];

export default function Workspace() {
  const [srcPreview, setSrcPreview] = useState<string|null>(null);
  const [refPreview, setRefPreview] = useState<string|null>(null);
  const [srcName,    setSrcName]    = useState('');
  const [refName,    setRefName]    = useState('');
  const [srcFile,    setSrcFile]    = useState<File|null>(null);
  const [refFile,    setRefFile]    = useState<File|null>(null);

  // Core pipeline state
  const [phase,    setPhase]    = useState<'idle'|'running'|'done'|'error'>('idle');
  const [stage,    setStage]    = useState(0);
  const [logs,     setLogs]     = useState<{ts:string;level:string;msg:string}[]>([]);
  const [metrics,  setMetrics]  = useState<Record<string,any>|null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [ts,       setTs]       = useState(0); // image cache-buster

  // UI extras
  const [lightbox,     setLightbox]     = useState<typeof PRODUCTS[0]|null>(null);
  const [compareMode,  setCompareMode]  = useState(false);
  const [opacity,      setOpacity]      = useState(50);

  const logRef  = useRef<HTMLDivElement>(null);
  const [runId, setRunId] = useState<string>('');
  const seenRef  = useRef(0);

  // Auto-scroll logs
  useEffect(() => { logRef.current?.scrollTo(0, logRef.current.scrollHeight); }, [logs]);

  // ── POLL LOOP ─────────────────────────────────────────────────────
  // Only active while phase === 'running' and a run ID has arrived
  useEffect(() => {
    if (phase !== 'running' || !runId) return;

    const id = runId;
    let dead = false;

    const tick = async () => {
      if (dead) return;
      try {
        const [sRes, eRes] = await Promise.all([
          fetch(`/api/run/${id}/status`).then(r => r.json()),
          fetch(`/api/run/${id}/events`).then(r => r.json()),
        ]);

        // Update stage
        if (typeof sRes.stage === 'number' && sRes.stage > 0) {
          setStage(sRes.stage);
        }

        // Append new logs
        const all: {ts:string;level:string;msg:string}[] = eRes.events ?? [];
        if (all.length > seenRef.current) {
          const newLines = all.slice(seenRef.current);
          seenRef.current = all.length;
          setLogs(prev => [...prev, ...newLines]);
        }

        // Check completion
        if (sRes.status === 'COMPLETE') {
          dead = true;
          setStage(10);
          setMetrics(sRes.metrics ?? null);
          setTs(Date.now());
          setPhase('done');
        } else if (sRes.status === 'ERROR') {
          dead = true;
          setErrorMsg('Pipeline returned ERROR — check log panel');
          setPhase('error');
        }
      } catch (e) {
        // network glitch — keep retrying
      }

      if (!dead) setTimeout(tick, 700);
    };

    setTimeout(tick, 700);

    return () => { dead = true; };
  }, [phase, runId]);

  // ── RUN ──────────────────────────────────────────────────────────
  const run = async () => {
    if (!srcPreview || !refPreview || phase === 'running') return;

    setRunId('');
    seenRef.current  = 0;
    setPhase('running');
    setStage(1);
    setLogs([{ ts: now(), level: 'INFO', msg: 'Connecting to LunarMatch-X engine...' }]);
    setMetrics(null);
    setErrorMsg('');

    try {
      // Upload if actual files were picked
      let srcPath = '', refPath = '';
      if (srcFile) {
        const fd = new FormData(); fd.append('file', srcFile);
        const r = await fetch('/api/upload/source', { method:'POST', body:fd }).then(r=>r.json());
        srcPath = r.path ?? '';
        addLog('INFO', `Uploaded: ${srcFile.name}`);
      }
      if (refFile) {
        const fd = new FormData(); fd.append('file', refFile);
        const r = await fetch('/api/upload/reference', { method:'POST', body:fd }).then(r=>r.json());
        refPath = r.path ?? '';
        addLog('INFO', `Uploaded: ${refFile.name}`);
      }

      // Start run
      const qs = new URLSearchParams();
      if (srcPath) qs.set('source_path', srcPath);
      if (refPath) qs.set('reference_path', refPath);
      const res = await fetch(`/api/run?${qs}`, { method:'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status} from backend`);
      const body = await res.json();
      setRunId(body.run_id);
      addLog('INFO', `Pipeline started · run ID: ${body.run_id}`);

    } catch (e: any) {
      setErrorMsg(e?.message ?? 'Failed to reach backend');
      setPhase('error');
    }
  };

  const reset = () => {
    setRunId('');
    seenRef.current  = 0;
    setPhase('idle'); setStage(0); setLogs([]); setMetrics(null); setErrorMsg('');
  };

  const addLog = (level: string, msg: string) =>
    setLogs(prev => [...prev, { ts: now(), level, msg }]);

  function now() { return new Date().toISOString().slice(11,19); }

  // ── DERIVED STYLE ────────────────────────────────────────────────
  const badgeCls =
    phase==='running' ? 'text-yellow-400 border-yellow-500 bg-yellow-500/10 animate-pulse' :
    phase==='done'    ? 'text-green-400 border-green-500 bg-green-500/10' :
    phase==='error'   ? 'text-red-400 border-red-500 bg-red-500/10' :
                        'text-[#00e5ff] border-[#00e5ff]/40 bg-[#00e5ff]/5';

  const badgeLabel =
    phase==='running' ? 'PROCESSING...' :
    phase==='done'    ? '✓ COMPLETE' :
    phase==='error'   ? 'ERROR' : 'PIPELINE READY';

  const decColor =
    metrics?.decision==='ACCEPT' ? 'text-green-400 border-green-500 bg-green-500/10' :
    metrics?.decision==='FLAG'   ? 'text-yellow-400 border-yellow-500 bg-yellow-500/10' :
                                   'text-red-400 border-red-500 bg-red-500/10';

  return (
    <>
      {/* LIGHTBOX */}
      {lightbox && (
        <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-6"
          onClick={() => setLightbox(null)}>
          <div className="relative max-w-5xl w-full bg-[#0a1128] border border-[#3a506b] rounded-xl p-4"
            onClick={e => e.stopPropagation()}>
            <button className="absolute top-3 right-3 text-gray-400 hover:text-white"
              onClick={() => setLightbox(null)}><X size={22}/></button>
            <div className="flex items-center gap-2 mb-3">
              <p className="text-sm font-bold text-[#00e5ff]">{lightbox.label}</p>
              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${lightbox.sc}`}>{lightbox.status}</span>
            </div>
            <img src={`${lightbox.src}?t=${ts}`} className="w-full max-h-[72vh] object-contain rounded bg-black"/>
            <p className="text-xs text-gray-500 mt-2">{lightbox.cap}</p>
          </div>
        </div>
      )}

      <div className="relative flex flex-col h-full overflow-hidden">
        {/* TOP BAR */}
        <div className="relative z-10 flex items-center justify-between px-8 py-4 border-b border-[#3a506b] bg-[#1c2541]/90 backdrop-blur-sm shrink-0">
          <div>
            <h1 className="font-display text-2xl font-bold text-white tracking-wider">LUNARMATCH-X</h1>
            <p className="text-[10px] text-gray-400 uppercase tracking-widest">Unified Physics-Aware Lunar Correspondence Pipeline</p>
          </div>
          <span className={`text-xs font-bold px-3 py-1.5 rounded border ${badgeCls}`}>{badgeLabel}</span>
        </div>

        <div className="relative z-10 flex flex-1 overflow-hidden">

          {/* MAIN SCROLL AREA */}
          <div className="flex-1 overflow-y-auto p-6 space-y-5">

            {/* INPUT CARDS */}
            <div className="grid grid-cols-2 gap-4">
              <DropCard title="SOURCE IMAGE" badge="OHRC · PAN · 0.25 m/px" badgeCls="text-[#00e5ff]"
                preview={srcPreview} name={srcName} onChange={e => {
                  const f = e.target.files?.[0]; if(!f) return;
                  setSrcPreview(URL.createObjectURL(f)); setSrcName(f.name); setSrcFile(f);
                }}/>
              <DropCard title="REFERENCE ARCHIVE" badge="LRO NAC · 1.212 m/px" badgeCls="text-green-400"
                preview={refPreview} name={refName} onChange={e => {
                  const f = e.target.files?.[0]; if(!f) return;
                  setRefPreview(URL.createObjectURL(f)); setRefName(f.name); setRefFile(f);
                }}/>
            </div>

            {/* ACTION ROW */}
            <div className="flex items-center gap-3 flex-wrap">
              <button onClick={() => {
                  setSrcPreview('/real-data/ohrc_input.png');
                  setRefPreview('/real-data/lro_input.png');
                  setSrcName('ch2_ohr_ncp_20260103T1005176450  [OHRC crop · 0.25 m/px]');
                  setRefName('M176219771RE.IMG  [LRO NAC crop · 1.212 m/px]');
                  setSrcFile(null); setRefFile(null);
                }}
                className="px-4 py-2 bg-[#3a506b] hover:bg-[#4a6585] text-sm text-white rounded-lg font-semibold transition-colors">
                Load Phase 2.2 Real Data
              </button>

              <button onClick={run}
                disabled={!srcPreview || !refPreview || phase==='running'}
                className="flex items-center gap-2 px-8 py-2.5 bg-[#00e5ff] text-black font-bold rounded-lg hover:bg-[#18ffff] disabled:opacity-40 transition-colors shadow-[0_0_20px_rgba(0,229,255,0.18)]">
                <Play size={16}/>
                {phase==='running' ? 'RUNNING...' : 'RUN LUNARMATCH-X'}
              </button>

              {phase !== 'idle' && (
                <button onClick={reset}
                  className="flex items-center gap-1.5 px-4 py-2.5 text-sm text-gray-400 hover:text-white border border-[#3a506b] rounded-lg transition-colors">
                  <RotateCcw size={14}/> Reset
                </button>
              )}

              {phase === 'done' && (
                <button onClick={() => setCompareMode(c=>!c)}
                  className={`flex items-center gap-1.5 px-4 py-2.5 text-sm rounded-lg border transition-colors
                    ${compareMode ? 'bg-[#00e5ff]/15 border-[#00e5ff] text-[#00e5ff]' : 'border-[#3a506b] text-gray-400 hover:text-white'}`}>
                  <Layers size={14}/> Compare View
                </button>
              )}
            </div>

            {/* ERROR BANNER */}
            {phase==='error' && errorMsg && (
              <div className="bg-red-500/10 border border-red-500/40 rounded-lg p-4 text-sm text-red-400">
                ⚠ {errorMsg}
              </div>
            )}

            {/* COMPARE OVERLAY */}
            {phase==='done' && compareMode && (
              <div className="bg-[#1c2541] border border-[#3a506b] rounded-xl p-4">
                <div className="flex items-center gap-3 mb-3">
                  <SlidersHorizontal size={15} className="text-[#00e5ff]"/>
                  <span className="text-sm font-bold text-white">OHRC ↔ LRO Overlay</span>
                  <span className="text-xs text-gray-500 ml-auto">opacity: {opacity}%</span>
                </div>
                <input type="range" min={0} max={100} value={opacity}
                  onChange={e=>setOpacity(+e.target.value)}
                  className="w-full accent-[#00e5ff] mb-3"/>
                <div className="relative h-64 bg-black rounded overflow-hidden border border-[#3a506b]">
                  <img src={`/api/outputs/registered_image.png?t=${ts}`} className="absolute inset-0 w-full h-full object-contain"/>
                  <img src={`/api/outputs/matched_tiepoints.png?t=${ts}`}
                    className="absolute inset-0 w-full h-full object-contain transition-opacity duration-100"
                    style={{opacity:opacity/100}}/>
                  <span className="absolute bottom-2 left-2 text-[10px] text-white bg-black/70 px-2 py-0.5 rounded">Registered base</span>
                  <span className="absolute bottom-2 right-2 text-[10px] text-[#00e5ff] bg-black/70 px-2 py-0.5 rounded">Tie-points overlay</span>
                </div>
              </div>
            )}

            {/* PIPELINE STAGES — visible once running starts */}
            {phase !== 'idle' && (
              <div className="bg-[#1c2541] border border-[#3a506b] rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-gray-200 text-sm tracking-wider">10-STAGE PIPELINE</h3>
                  {metrics && (
                    <span className={`text-xs font-bold px-3 py-1 rounded border ${decColor}`}>
                      DECISION: {metrics.decision}
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-5 gap-2">
                  {STAGES.map(s => {
                    const done   = stage > s.id;
                    const active = stage === s.id && phase === 'running';
                    const final  = stage === s.id && phase === 'done';
                    return (
                      <div key={s.id} className={`relative border rounded-lg p-3 transition-all duration-300
                        ${done||final ? 'border-green-500/40 bg-green-500/5'
                        : active     ? 'border-[#00e5ff] shadow-[0_0_10px_rgba(0,229,255,0.15)] bg-[#00e5ff]/5'
                        :              'border-[#3a506b] opacity-40'}`}>
                        {!s.real && <div className="absolute -top-2 -right-2 text-[8px] font-bold bg-amber-500 text-black px-1 rounded">NEXT</div>}
                        <div className="flex items-center gap-1 mb-1.5">
                          {(done||final) && <CheckCircle2 size={10} className="text-green-500 shrink-0"/>}
                          {active        && <CircleDashed  size={10} className="text-[#00e5ff] animate-spin shrink-0"/>}
                          {!done&&!active&&!final && <Circle size={10} className="text-gray-600 shrink-0"/>}
                          <span className="text-[8px] text-gray-600 font-mono">S{s.id}</span>
                        </div>
                        <p className={`text-[9px] font-semibold leading-tight
                          ${done||final ? 'text-green-400' : active ? 'text-[#00e5ff]' : 'text-gray-500'}`}>
                          {s.label}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* METRICS STRIP */}
            {metrics && (
              <div className="grid grid-cols-5 gap-3">
                {[
                  {l:'OHRC Keypoints',   v:metrics.ohrc_kp?.toLocaleString()??'—', s:'SIFT native'},
                  {l:'LRO Keypoints',    v:metrics.lro_kp?.toLocaleString()??'—',  s:'SIFT native'},
                  {l:'Candidates',       v:metrics.candidates,                       s:'Lowe 0.80'},
                  {l:'RANSAC Inliers',   v:metrics.inliers,                          s:`${metrics.inlier_ratio}%`},
                  {l:'Reprojection Err', v:`${metrics.reprojection_error_px} px`,    s:'mean Euclid'},
                ].map(m => (
                  <div key={m.l} className="bg-[#1c2541] border border-[#3a506b] rounded-lg p-3 text-center">
                    <div className="text-[9px] text-gray-500 uppercase tracking-wider leading-tight">{m.l}</div>
                    <div className="text-lg font-bold text-white mt-1">{m.v}</div>
                    <div className="text-[9px] text-gray-600 mt-0.5">{m.s}</div>
                  </div>
                ))}
              </div>
            )}

            {/* ═══ GENERATED IMAGES — shown the moment phase becomes 'done' ═══ */}
            {phase === 'done' && (
              <div className="bg-[#1c2541] border border-[#3a506b] rounded-xl p-5">
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-1 h-6 bg-[#00e5ff] rounded-full"/>
                  <div>
                    <h2 className="text-base font-bold text-white">Generated Images</h2>
                    <p className="text-[10px] text-gray-500">Real pipeline output products — click any image to enlarge</p>
                  </div>
                </div>

                {/* Row 1 — 3 cards */}
                <div className="grid grid-cols-3 gap-3 mb-3">
                  {PRODUCTS.slice(0,3).map(p => (
                    <ProdCard key={p.key} p={p} ts={ts} onClick={()=>setLightbox(p)}/>
                  ))}
                </div>

                {/* Row 2 — 2 centred cards */}
                <div className="flex justify-center gap-3">
                  {PRODUCTS.slice(3).map(p => (
                    <div key={p.key} className="w-[calc(33.33%-6px)]">
                      <ProdCard p={p} ts={ts} onClick={()=>setLightbox(p)}/>
                    </div>
                  ))}
                </div>

                <p className="mt-5 text-center text-[11px] text-gray-600 italic border-t border-[#3a506b] pt-4">
                  "Visual correspondence proposes.{' '}
                  <span className="text-gray-400">Physics verifies. Uncertainty decides.</span>"
                </p>
              </div>
            )}

          </div>{/* end main scroll */}

          {/* LIVE LOG PANEL */}
          <div className="w-72 bg-[#060d1c] border-l border-[#3a506b] flex flex-col shrink-0">
            <div className="p-3 border-b border-[#3a506b] flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                phase==='running' ? 'bg-green-500 animate-pulse' :
                phase==='done'    ? 'bg-green-600' :
                phase==='error'   ? 'bg-red-500' : 'bg-gray-700'}`}/>
              <span className="text-[10px] font-bold text-gray-400 tracking-widest uppercase">Live Telemetry</span>
              <span className="ml-auto text-[9px] text-gray-700 font-mono">{logs.length} lines</span>
            </div>
            <div ref={logRef} className="flex-1 overflow-y-auto p-3 font-mono text-[9px] leading-relaxed space-y-0.5">
              {logs.length===0 && <p className="text-gray-700 italic">Awaiting pipeline start...</p>}
              {logs.map((l,i) => (
                <div key={i} className={
                  l.level==='ERROR'    ? 'text-red-400 font-bold' :
                  l.level==='WARN'     ? 'text-amber-400' :
                  l.level==='COMPLETE' ? 'text-green-400 font-bold' :
                  l.level==='FLAG'     ? 'text-yellow-300 font-bold' :
                  l.level==='ACCEPT'   ? 'text-green-300 font-bold' :
                  l.level==='REFUSE'   ? 'text-red-300 font-bold' :
                  'text-green-400/70'
                }>
                  <span className="text-gray-700">[{l.ts}]</span> {l.msg}
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────

function DropCard({ title, badge, badgeCls, preview, name, onChange }:{
  title:string; badge:string; badgeCls:string;
  preview:string|null; name:string;
  onChange:(e:React.ChangeEvent<HTMLInputElement>)=>void;
}) {
  return (
    <div className="bg-[#1c2541] border border-[#3a506b] rounded-xl p-4 hover:border-[#00e5ff]/30 transition-colors">
      <div className="flex justify-between items-center mb-3">
        <h3 className={`text-xs font-bold ${badgeCls}`}>{title}</h3>
        <span className="text-[10px] text-gray-400 bg-[#0a1128] px-2 py-0.5 rounded font-mono">{badge}</span>
      </div>
      <label className="block border-2 border-dashed border-[#3a506b] rounded-lg h-44 relative overflow-hidden cursor-pointer hover:border-[#00e5ff] transition-colors group">
        {preview
          ? <img src={preview} className="w-full h-full object-contain bg-black"/>
          : <div className="w-full h-full flex flex-col items-center justify-center gap-2 text-gray-600 group-hover:text-gray-300 transition-colors">
              <Upload size={28}/>
              <span className="text-xs">Click or drag to upload</span>
              <span className="text-[10px] text-gray-700">.img · .png · .jpg · .tif</span>
            </div>
        }
        <input type="file" accept="image/*,.img,.IMG,.tif,.tiff"
          className="absolute inset-0 opacity-0 cursor-pointer" onChange={onChange}/>
      </label>
      {name && <p className="text-[9px] text-gray-600 mt-1.5 truncate font-mono">{name}</p>}
    </div>
  );
}

function ProdCard({ p, ts, onClick }:{ p:typeof PRODUCTS[0]; ts:number; onClick:()=>void }) {
  const [loaded,  setLoaded]  = useState(false);
  const [errored, setErrored] = useState(false);
  return (
    <div onClick={onClick}
      className="group bg-[#0a1128] border border-[#3a506b] rounded-lg overflow-hidden hover:border-[#00e5ff] cursor-pointer transition-all">
      <div className="relative h-44 bg-black overflow-hidden">
        {!errored
          ? <img src={`${p.src}?t=${ts}`}
              onLoad={()=>setLoaded(true)}
              onError={()=>setErrored(true)}
              className={`w-full h-full object-cover transition-all duration-300
                ${loaded ? 'opacity-85 group-hover:opacity-100 group-hover:scale-105' : 'opacity-0'}`}/>
          : <div className="w-full h-full flex items-center justify-center text-red-400/60 text-xs">Image not found</div>
        }
        {!loaded && !errored && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-5 h-5 border-2 border-[#00e5ff] border-t-transparent rounded-full animate-spin"/>
          </div>
        )}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/30">
          <ZoomIn size={26} className="text-white drop-shadow"/>
        </div>
        <span className={`absolute top-2 right-2 text-[9px] font-bold px-1.5 py-0.5 rounded border ${p.sc}`}>
          {p.status}
        </span>
      </div>
      <div className="p-3">
        <p className="text-xs font-semibold text-white">{p.label}</p>
        <p className="text-[9px] text-gray-500 mt-0.5 leading-snug">{p.cap}</p>
      </div>
    </div>
  );
}
