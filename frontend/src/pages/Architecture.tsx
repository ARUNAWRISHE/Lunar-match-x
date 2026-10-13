import { Database, Radar, Ruler, ScanSearch, ShieldCheck, GitBranch, Layers, Gauge, ArrowRight } from 'lucide-react';

const FLOW = [
  { icon: Database, label: 'Ingestion' },
  { icon: Ruler, label: 'GSD Normalize' },
  { icon: ScanSearch, label: 'SIFT Match' },
  { icon: ShieldCheck, label: 'RANSAC Verify' },
  { icon: Gauge, label: 'Decision' },
];

export default function Architecture() {
  const modules = [
    { name: 'Data Ingestion', icon: Database, status: 'REAL', desc: 'Parses PDS4 XML, PDS3 headers, extracts footprints, safely memmaps 100GB+ arrays.' },
    { name: 'Sensor Adapters', icon: Radar, status: 'PARTIAL', desc: 'Abstracts OHRC/LRO geometries. TMC-2 and IIRS planned.' },
    { name: 'Geometry Engine', icon: GitBranch, status: 'NEXT', desc: 'Currently uses 2D fallback. Next phase integrates NASA SPICE kernels and Lunar DEM.' },
    { name: 'Normalization Engine', icon: Ruler, status: 'REAL', desc: 'Rescales multi-resolution imagery to a common Target GSD (e.g. 0.25m -> 1.21m).' },
    { name: 'Multimodal Representation', icon: Layers, status: 'PLANNED', desc: 'Translates thermal/spectral/pan images into a unified feature space.' },
    { name: 'Matching Engine', icon: ScanSearch, status: 'REAL', desc: 'Robust SIFT/FLANN feature extraction and nearest-neighbor correspondence.' },
    { name: 'Geometric Verification', icon: ShieldCheck, status: 'REAL', desc: 'RANSAC homography estimation filtering outliers.' },
    { name: 'Uncertainty Engine', icon: Gauge, status: 'PARTIAL', desc: 'Accept/Flag/Refuse logic based on geometric consensus.' },
  ];

  return (
    <div className="h-full overflow-y-auto p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold mb-2">System Architecture</h1>
        <p className="text-gray-400">LunarMatch-X Unified Pipeline Design</p>
      </div>

      {/* Data-flow strip */}
      <div className="flex items-center justify-between bg-[#1c2541]/80 backdrop-blur-sm border border-[#3a506b] rounded-xl px-6 py-5 mb-8 overflow-x-auto">
        {FLOW.map((f, i) => (
          <div key={f.label} className="flex items-center gap-3 shrink-0">
            <div className="flex flex-col items-center gap-2">
              <div className="w-11 h-11 rounded-full bg-[#0a1128] border border-[#00e5ff]/40 flex items-center justify-center text-[#00e5ff]">
                <f.icon size={18} />
              </div>
              <span className="text-[10px] text-gray-400 tracking-wide whitespace-nowrap">{f.label}</span>
            </div>
            {i < FLOW.length - 1 && <ArrowRight size={16} className="text-[#3a506b] mx-2 shrink-0" />}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        {modules.map((m, i) => (
          <div key={i} className="bg-[#1c2541]/80 backdrop-blur-sm border border-[#3a506b] p-6 rounded-lg relative hover:border-[#00e5ff] transition-colors group">
            <div className="absolute top-4 right-4 text-[10px] font-bold px-2 py-1 rounded bg-black/50 border border-gray-600">
              {m.status === 'REAL' && <span className="text-green-400">IMPLEMENTED</span>}
              {m.status === 'PARTIAL' && <span className="text-yellow-400">PARTIAL</span>}
              {m.status === 'NEXT' && <span className="text-blue-400">NEXT PHASE</span>}
              {m.status === 'PLANNED' && <span className="text-gray-400">PLANNED</span>}
            </div>
            <div className="flex items-center gap-2.5 mb-2">
              <m.icon size={17} className="text-[#00e5ff]" />
              <h2 className="text-lg font-bold text-white group-hover:text-[#00e5ff] transition-colors">{m.name}</h2>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">{m.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
