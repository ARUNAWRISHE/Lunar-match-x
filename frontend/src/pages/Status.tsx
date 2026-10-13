const STATUS_LIST = [
  { component: 'OHRC ingestion (Real >1GB files)', status: 'REAL' },
  { component: 'LRO NAC ingestion (EDR parsing)', status: 'REAL' },
  { component: 'LRO footprint ODE archive search', status: 'REAL' },
  { component: 'Shapely footprint overlap detection', status: 'REAL' },
  { component: 'Common geographic ROI extraction', status: 'REAL' },
  { component: '2D geographic mapping & crop', status: 'REAL' },
  { component: 'Physical resolution normalization', status: 'REAL' },
  { component: 'SIFT Feature Matching', status: 'REAL' },
  { component: 'RANSAC Verification', status: 'REAL' },
  { component: 'SPICE geometric rigorous projection', status: 'NEXT' },
  { component: 'DEM terrain relief correction', status: 'PLANNED' },
  { component: 'Multimodal pan-to-spectral representation', status: 'PLANNED' },
  { component: 'Sub-pixel phase correlation refinement', status: 'PLANNED' },
  { component: 'Accept/Flag/Refuse uncertainty engine', status: 'PARTIAL' },
  { component: 'Automatic full-containment archive search', status: 'NEXT' },
  { component: 'TMC-2 pipeline branch', status: 'PLANNED' },
  { component: 'IIRS pipeline branch', status: 'PLANNED' },
  { component: 'SELENE pipeline branch', status: 'PLANNED' },
];

const BADGE: Record<string, string> = {
  REAL:    'bg-green-500/20 text-green-400 border-green-500/50',
  PARTIAL: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
  NEXT:    'bg-blue-500/20 text-blue-400 border-blue-500/50',
  PLANNED: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
};

const LABEL: Record<string, string> = {
  REAL: 'REAL / IMPLEMENTED',
  PARTIAL: 'PARTIAL',
  NEXT: 'NEXT PHASE',
  PLANNED: 'PLANNED',
};

export default function Status() {
  const counts = STATUS_LIST.reduce<Record<string, number>>((acc, s) => {
    acc[s.status] = (acc[s.status] ?? 0) + 1;
    return acc;
  }, {});
  const total = STATUS_LIST.length;

  return (
    <div className="h-full overflow-y-auto p-8 max-w-4xl mx-auto flex flex-col">
      <div className="mb-6">
        <h1 className="font-display text-3xl font-bold mb-2">Implementation Status</h1>
        <p className="text-gray-400">Current state of the LunarMatch-X codebase</p>
      </div>

      {/* Summary strip */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        {(['REAL', 'PARTIAL', 'NEXT', 'PLANNED'] as const).map((k) => (
          <div key={k} className="bg-[#1c2541]/80 backdrop-blur-sm border border-[#3a506b] rounded-lg p-3 text-center">
            <div className="text-2xl font-display font-bold text-white">{counts[k] ?? 0}</div>
            <div className={`inline-block mt-1 text-[9px] font-bold px-1.5 py-0.5 rounded border ${BADGE[k]}`}>{LABEL[k]}</div>
          </div>
        ))}
      </div>
      <div className="w-full h-1.5 rounded-full bg-[#1c2541] overflow-hidden mb-8 flex">
        <div className="h-full bg-green-500" style={{ width: `${((counts.REAL ?? 0) / total) * 100}%` }} />
        <div className="h-full bg-yellow-500" style={{ width: `${((counts.PARTIAL ?? 0) / total) * 100}%` }} />
        <div className="h-full bg-blue-500" style={{ width: `${((counts.NEXT ?? 0) / total) * 100}%` }} />
        <div className="h-full bg-gray-500" style={{ width: `${((counts.PLANNED ?? 0) / total) * 100}%` }} />
      </div>

      <div className="bg-[#1c2541]/80 backdrop-blur-sm border border-[#3a506b] rounded-lg overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-[#0a1128] sticky top-0 border-b border-[#3a506b] z-10">
            <tr>
              <th className="py-4 px-6 font-semibold text-gray-300">Component</th>
              <th className="py-4 px-6 font-semibold text-gray-300 text-right">Status</th>
            </tr>
          </thead>
          <tbody>
            {STATUS_LIST.map((item, idx) => (
              <tr key={idx} className="border-b border-[#3a506b]/50 hover:bg-white/5 transition-colors">
                <td className="py-4 px-6 text-gray-200">{item.component}</td>
                <td className="py-4 px-6 text-right">
                  <span className={`px-2 py-1 rounded text-[10px] font-bold border ${BADGE[item.status]}`}>{LABEL[item.status]}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
