import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ResultsDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch('/phase2/phase2_2_report.json')
      .then(res => res.json())
      .then(json => setData(json))
      .catch(err => console.error(err));
  }, []);

  if (!data) {
    return <div className="text-white p-8">Loading Real Results...</div>;
  }

  const isAccept = data.decision === 'ACCEPT';
  const decisionColor = isAccept ? 'text-green-500' : (data.decision === 'FLAG' ? 'text-yellow-500' : 'text-red-500');

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Phase 2.2 Analysis Complete</h1>
        <div className="flex gap-4 text-gray-400">
          <span>Source: <strong className="text-white">{data.ohrc_product}</strong></span>
          <span>|</span>
          <span>Reference: <strong className="text-white">{data.lro_product}</strong></span>
          <span>|</span>
          <span className={`${decisionColor} font-bold`}>{data.decision}</span>
        </div>
      </div>

      {/* Visual Diagnostics */}
      <div className="grid grid-cols-2 gap-6 mb-12">
        <div className="bg-[#1c2541] border border-[#3a506b] p-4 rounded-lg">
          <h2 className="text-xl font-bold mb-4 text-white">Geographic Footprint Intersection</h2>
          <img src="/phase2/footprints_diagnostic.png" alt="Footprints" className="w-full h-auto rounded" />
        </div>
        <div className="bg-[#1c2541] border border-[#3a506b] p-4 rounded-lg">
          <h2 className="text-xl font-bold mb-4 text-white">Physically Aligned ROIs</h2>
          <img src="/phase2/side_by_side_diagnostic.png" alt="Side by Side" className="w-full h-auto rounded" />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6 mb-12">
        {[
          { label: 'Candidates', value: data.candidate_matches, color: 'text-white' },
          { label: 'Verified', value: data.verified_matches, color: 'text-green-400' },
          { label: 'Decision', value: data.decision, color: decisionColor },
          { label: 'Reprojection Error', value: data.reprojection_error ? `${data.reprojection_error} px` : 'N/A', color: 'text-red-400' }
        ].map(stat => (
          <div key={stat.label} className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg text-center">
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">{stat.label}</div>
            <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-6 mb-12">
        {[
          { label: 'OHRC Keypoints', value: data.sift_keypoints_ohrc },
          { label: 'LRO Keypoints', value: data.sift_keypoints_lro },
          { label: 'Intersection Area', value: `${(data.intersection_area).toFixed(4)} sq deg` },
          { label: 'Target GSD', value: `${data.target_gsd} m/px` }
        ].map(stat => (
          <div key={stat.label} className="bg-[#0a1128] border border-[#3a506b] p-6 rounded-lg text-center relative">
            <div className="absolute top-2 right-2 text-[10px] text-green-500 font-bold">REAL DATA</div>
            <div className="text-xs text-[#00e5ff] uppercase tracking-wider mb-2">{stat.label}</div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-[#1c2541] border border-[#3a506b] rounded-lg p-8 mb-8">
        <h2 className="text-xl font-bold mb-6 text-white">Export Outputs</h2>
        <div className="flex gap-4">
          <a href="/phase2/phase2_2_report.json" target="_blank" className="flex-1 text-center bg-[#3a506b] hover:bg-[#4a6585] text-white py-3 rounded-lg font-semibold transition-colors">
            Raw JSON Report
          </a>
          <a href="/phase2/side_by_side_diagnostic.png" target="_blank" className="flex-1 text-center bg-[#3a506b] hover:bg-[#4a6585] text-white py-3 rounded-lg font-semibold transition-colors">
            Cropped Images
          </a>
          <button className="flex-1 bg-[#00e5ff] hover:bg-[#18ffff] text-black py-3 rounded-lg font-bold transition-colors shadow-[0_0_15px_rgba(0,229,255,0.3)]">
            Download Full Bundle
          </button>
        </div>
      </div>
      
      <div className="text-center">
         <button onClick={() => navigate('/dashboard')} className="text-gray-400 hover:text-white underline">
            Return to Dashboard
         </button>
      </div>
    </div>
  );
}
