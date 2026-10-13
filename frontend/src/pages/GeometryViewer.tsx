import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function GeometryViewer() {
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch('/phase2/phase2_2_report.json')
      .then(res => res.json())
      .then(json => setData(json))
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div className="text-white p-8">Loading...</div>;

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Geometry Constraints</h1>
        <p className="text-gray-400">Phase 2.2: 2D Geographic Footprint Approximation</p>
      </div>

      <div className="flex-1 grid grid-cols-3 gap-6 mb-6">
        <div className="col-span-2 bg-[#1c2541] border border-[#3a506b] rounded-lg flex flex-col items-center justify-center relative overflow-hidden p-4">
          <div className="absolute top-4 left-4 bg-black/50 px-3 py-1 rounded text-xs text-green-400 border border-green-400/30">
            REAL GEOGRAPHIC FOOTPRINTS
          </div>
          <img src="/phase2/footprints_diagnostic.png" className="h-full w-auto object-contain" />
        </div>

        <div className="col-span-1 flex flex-col gap-6 overflow-y-auto">
          <div className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg">
            <h3 className="text-[#00e5ff] font-bold mb-4">INTERSECTION ROIs</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Status:</span> <span className="text-yellow-400 font-bold">{data.overlap_status}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Area:</span> <span>{data.intersection_area.toFixed(4)} sq deg</span></div>
            </div>
          </div>
          
          <div className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg">
            <h3 className="text-[#00e5ff] font-bold mb-4">OHRC MAPPING</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Product:</span> <span>{data.ohrc_product.substring(0,20)}...</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Pixels X:</span> <span>~3579 to 8765</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Pixels Y:</span> <span>~40149 to 46902</span></div>
            </div>
          </div>
          
          <div className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg">
            <h3 className="text-[#00e5ff] font-bold mb-4">LRO NAC MAPPING</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Product:</span> <span>{data.lro_product}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Pixels X:</span> <span>~606 to 1910</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Pixels Y:</span> <span>~6106 to 6941</span></div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button 
          onClick={() => navigate('/analysis/latest/results')}
          className="bg-[#00e5ff] text-black px-6 py-2 rounded font-bold hover:bg-[#18ffff]"
        >
          Final Results &rarr;
        </button>
      </div>
    </div>
  );
}
