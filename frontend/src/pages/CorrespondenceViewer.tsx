import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function CorrespondenceViewer() {
  const [filter, setFilter] = useState('All');
  const [data, setData] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/phase2/phase2_2_report.json')
      .then(res => res.json())
      .then(json => setData(json))
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div className="text-white p-8">Loading Real Data...</div>;

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Correspondence Viewer</h1>
          <p className="text-green-400 font-bold">REAL PHASE 2.2 DATA</p>
        </div>
        <div className="flex gap-2">
          {['All', 'Verified', 'Flagged', 'Rejected'].map(f => (
            <button 
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded text-sm font-semibold transition-colors ${filter === f ? 'bg-[#00e5ff] text-black' : 'bg-[#1c2541] text-gray-300 hover:bg-[#3a506b]'}`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 grid grid-cols-2 gap-8 mb-6">
        {/* Source Image */}
        <div className="bg-[#1c2541] border border-[#3a506b] rounded-lg p-4 flex flex-col">
          <h3 className="font-semibold text-gray-300 mb-2">SOURCE [OHRC ROI - Scaled]</h3>
          <div className="flex-1 bg-black rounded relative overflow-hidden flex items-center justify-center border border-[#3a506b]">
            <img src="/real-data/ohrc_crop.png" className="w-full h-full object-contain opacity-90" />
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
               <span className="text-white opacity-50 text-xs">Matches detected by SIFT plotted here</span>
            </div>
          </div>
        </div>

        {/* Reference Image */}
        <div className="bg-[#1c2541] border border-[#3a506b] rounded-lg p-4 flex flex-col">
          <h3 className="font-semibold text-gray-300 mb-2">REFERENCE [LRO NAC ROI]</h3>
          <div className="flex-1 bg-black rounded relative overflow-hidden flex items-center justify-center border border-[#3a506b]">
            <img src="/real-data/lro_crop.png" className="w-full h-full object-contain opacity-90" />
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
               <span className="text-white opacity-50 text-xs">Matches detected by SIFT plotted here</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-[#1c2541] border border-[#3a506b] rounded-lg p-4 flex justify-between items-center text-sm">
        <div className="flex gap-8">
          <span className="text-gray-400">{data.candidate_matches} Candidates</span>
          <span className="text-green-400 font-bold">{data.verified_matches} Verified Inliers</span>
          <span className="text-yellow-400 font-bold">{data.candidate_matches - data.verified_matches} Rejected by RANSAC</span>
        </div>
        <button 
          onClick={() => navigate('/analysis/latest/geometry')}
          className="bg-[#00e5ff] text-black px-6 py-2 rounded font-bold hover:bg-[#18ffff]"
        >
          View Geometry &rarr;
        </button>
      </div>
    </div>
  );
}
