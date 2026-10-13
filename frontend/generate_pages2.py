import os

components = {
    'src/pages/CorrespondenceViewer.tsx': '''import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function CorrespondenceViewer() {
  const [filter, setFilter] = useState('All');
  const navigate = useNavigate();

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Correspondence Viewer</h1>
          <p className="text-gray-400">ID: LMX-025 - SIMULATED RESULTS</p>
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
          <h3 className="font-semibold text-gray-300 mb-2">SOURCE [OHRC]</h3>
          <div className="flex-1 bg-black rounded relative overflow-hidden flex items-center justify-center border border-[#3a506b]">
            <img src="/demo-data/ohrc_demo.jpg" className="w-full h-full object-cover opacity-80" />
            <div className="absolute inset-0 pointer-events-none">
              {/* Simulated Points */}
              {(filter === 'All' || filter === 'Verified') && <div className="absolute top-[40%] left-[30%] w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_#22c55e]" />}
              {(filter === 'All' || filter === 'Verified') && <div className="absolute top-[60%] left-[70%] w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_#22c55e]" />}
              {(filter === 'All' || filter === 'Flagged') && <div className="absolute top-[20%] left-[50%] w-2 h-2 bg-yellow-500 rounded-full shadow-[0_0_8px_#eab308]" />}
              {(filter === 'All' || filter === 'Rejected') && <div className="absolute top-[80%] left-[40%] w-2 h-2 bg-red-500 rounded-full shadow-[0_0_8px_#ef4444]" />}
            </div>
          </div>
        </div>

        {/* Reference Image */}
        <div className="bg-[#1c2541] border border-[#3a506b] rounded-lg p-4 flex flex-col">
          <h3 className="font-semibold text-gray-300 mb-2">REFERENCE [LRO NAC]</h3>
          <div className="flex-1 bg-black rounded relative overflow-hidden flex items-center justify-center border border-[#3a506b]">
            <img src="/demo-data/lro_nac_demo.jpg" className="w-full h-full object-cover opacity-80" />
            <div className="absolute inset-0 pointer-events-none">
              {/* Simulated Points */}
              {(filter === 'All' || filter === 'Verified') && <div className="absolute top-[42%] left-[32%] w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_#22c55e]" />}
              {(filter === 'All' || filter === 'Verified') && <div className="absolute top-[62%] left-[72%] w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_#22c55e]" />}
              {(filter === 'All' || filter === 'Flagged') && <div className="absolute top-[22%] left-[52%] w-2 h-2 bg-yellow-500 rounded-full shadow-[0_0_8px_#eab308]" />}
              {(filter === 'All' || filter === 'Rejected') && <div className="absolute top-[10%] left-[80%] w-2 h-2 bg-red-500 rounded-full shadow-[0_0_8px_#ef4444]" />}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-[#1c2541] border border-[#3a506b] rounded-lg p-4 flex justify-between items-center text-sm">
        <div className="flex gap-8">
          <span className="text-gray-400">142 Candidates</span>
          <span className="text-green-400 font-bold">97 Verified</span>
          <span className="text-yellow-400 font-bold">28 Flagged</span>
          <span className="text-red-400 font-bold">17 Rejected</span>
        </div>
        <button 
          onClick={() => navigate('/analysis/LMX-025/geometry')}
          className="bg-[#00e5ff] text-black px-6 py-2 rounded font-bold hover:bg-[#18ffff]"
        >
          View Geometry &rarr;
        </button>
      </div>
    </div>
  );
}
''',
    'src/pages/GeometryViewer.tsx': '''import { useNavigate } from 'react-router-dom';

export default function GeometryViewer() {
  const navigate = useNavigate();

  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Geometry Constraints</h1>
        <p className="text-gray-400">Simulated 3D terrain and spacecraft raycasting</p>
      </div>

      <div className="flex-1 grid grid-cols-3 gap-6 mb-6">
        <div className="col-span-2 bg-[#1c2541] border border-[#3a506b] rounded-lg flex items-center justify-center relative overflow-hidden">
          <div className="absolute top-4 left-4 bg-black/50 px-3 py-1 rounded text-xs text-yellow-400 border border-yellow-400/30">
            SIMULATED 3D RENDER
          </div>
          {/* Mockup of a 3D scene without actually loading three.js models for brevity */}
          <div className="w-64 h-64 border-4 border-dashed border-[#00e5ff] rounded-full flex items-center justify-center opacity-20">
            <span className="text-[#00e5ff] font-bold text-xl">LUNAR DEM MOCKUP</span>
          </div>
          
          <div className="absolute top-1/4 left-1/2 w-px h-1/2 bg-gradient-to-b from-yellow-400 to-transparent shadow-[0_0_10px_#eab308]" />
          <div className="absolute top-1/4 left-1/2 -ml-2 w-4 h-4 bg-white rounded flex items-center justify-center text-black text-[8px] font-bold">SAT</div>
        </div>

        <div className="col-span-1 flex flex-col gap-6">
          <div className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg">
            <h3 className="text-[#00e5ff] font-bold mb-4">SPACECRAFT</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Altitude:</span> <span>100 km</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Attitude:</span> <span>Stable</span></div>
              <div className="flex justify-between"><span className="text-gray-400">View Angle:</span> <span>24.8&deg;</span></div>
            </div>
          </div>
          
          <div className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg">
            <h3 className="text-[#00e5ff] font-bold mb-4">GEOMETRY</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Incidence:</span> <span>63.2&deg;</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Emission:</span> <span>11.4&deg;</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Phase:</span> <span>58.7&deg;</span></div>
            </div>
          </div>
          
          <div className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg">
            <h3 className="text-[#00e5ff] font-bold mb-4">TERRAIN</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Elevation:</span> <span>1,842 m</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Local Slope:</span> <span>14.2&deg;</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Relief:</span> <span>Moderate</span></div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button 
          onClick={() => navigate('/analysis/LMX-025/results')}
          className="bg-[#00e5ff] text-black px-6 py-2 rounded font-bold hover:bg-[#18ffff]"
        >
          Final Results &rarr;
        </button>
      </div>
    </div>
  );
}
''',
    'src/pages/ResultsDashboard.tsx': '''import { useNavigate } from 'react-router-dom';

export default function ResultsDashboard() {
  const navigate = useNavigate();

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Analysis Complete</h1>
        <div className="flex gap-4 text-gray-400">
          <span>Source: <strong className="text-white">OHRC</strong></span>
          <span>|</span>
          <span>Reference: <strong className="text-white">LRO NAC</strong></span>
          <span>|</span>
          <span className="text-green-500 font-bold">COMPLETED</span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6 mb-12">
        {[
          { label: 'Candidates', value: '142', color: 'text-white' },
          { label: 'Verified', value: '97', color: 'text-green-400' },
          { label: 'Flagged', value: '28', color: 'text-yellow-400' },
          { label: 'Rejected', value: '17', color: 'text-red-400' }
        ].map(stat => (
          <div key={stat.label} className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg text-center">
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">{stat.label}</div>
            <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-6 mb-12">
        {[
          { label: 'RMSE', value: '0.64 px' },
          { label: 'Inlier Ratio', value: '78.4%' },
          { label: 'Coverage', value: '86.2%' },
          { label: 'Median Uncertainty', value: '0.18 px' }
        ].map(stat => (
          <div key={stat.label} className="bg-[#0a1128] border border-[#3a506b] p-6 rounded-lg text-center relative">
            <div className="absolute top-2 right-2 text-[10px] text-gray-600 font-bold">SIMULATED</div>
            <div className="text-xs text-[#00e5ff] uppercase tracking-wider mb-2">{stat.label}</div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-[#1c2541] border border-[#3a506b] rounded-lg p-8 mb-8">
        <h2 className="text-xl font-bold mb-6">Export Outputs</h2>
        <div className="flex gap-4">
          <button className="flex-1 bg-[#3a506b] hover:bg-[#4a6585] text-white py-3 rounded-lg font-semibold transition-colors">
            Registered Image
          </button>
          <button className="flex-1 bg-[#3a506b] hover:bg-[#4a6585] text-white py-3 rounded-lg font-semibold transition-colors">
            Matched Tie-Points
          </button>
          <button className="flex-1 bg-[#3a506b] hover:bg-[#4a6585] text-white py-3 rounded-lg font-semibold transition-colors">
            Uncertainty Map
          </button>
          <button className="flex-1 bg-[#00e5ff] hover:bg-[#18ffff] text-black py-3 rounded-lg font-bold transition-colors shadow-[0_0_15px_rgba(0,229,255,0.3)]">
            Download Full Report
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
'''
}

for path, content in components.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
