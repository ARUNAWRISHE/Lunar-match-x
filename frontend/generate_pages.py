import os

components = {
    'src/pages/Dashboard.tsx': '''import { Link } from 'react-router-dom';

export default function Dashboard() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">LunarMatch-X</h1>
        <h2 className="text-xl text-gray-400">Unified Physics-Aware Lunar Correspondence</h2>
        <p className="mt-4 text-gray-500 max-w-2xl">Cross-sensor lunar image correspondence with geometry-aware verification.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        {[
          { label: 'Analyses', value: '24', color: 'text-white' },
          { label: 'Verified Matches', value: '1,842', color: 'text-green-400' },
          { label: 'Flagged Matches', value: '317', color: 'text-yellow-400' },
          { label: 'Rejected Matches', value: '126', color: 'text-red-400' }
        ].map(stat => (
          <div key={stat.label} className="bg-[#1c2541] border border-[#3a506b] p-6 rounded-lg shadow-lg relative overflow-hidden">
            <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{stat.label}</div>
            <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="absolute top-2 right-2 text-[10px] text-gray-600 font-bold bg-black/20 px-2 py-1 rounded">DEMO DATA</div>
          </div>
        ))}
      </div>

      <div className="flex justify-between items-end mb-6">
        <h3 className="text-xl font-semibold text-white">Recent Analyses</h3>
        <Link to="/new" className="bg-[#00e5ff] text-black px-6 py-2 rounded font-bold hover:bg-[#18ffff] transition-colors shadow-[0_0_15px_rgba(0,229,255,0.4)]">
          + New Analysis
        </Link>
      </div>

      <div className="bg-[#1c2541] border border-[#3a506b] rounded-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-[#0a1128] border-b border-[#3a506b]">
            <tr>
              <th className="p-4 text-gray-400 text-sm">Analysis ID</th>
              <th className="p-4 text-gray-400 text-sm">Source</th>
              <th className="p-4 text-gray-400 text-sm">Reference</th>
              <th className="p-4 text-gray-400 text-sm">Status</th>
              <th className="p-4 text-gray-400 text-sm">Matches</th>
              <th className="p-4 text-gray-400 text-sm">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#3a506b]">
            {[
              { id: 'LMX-024', src: 'OHRC', ref: 'LRO NAC', status: 'Completed', matches: 97, date: '2023-10-15' },
              { id: 'LMX-023', src: 'IIRS', ref: 'LRO WAC', status: 'Completed', matches: 64, date: '2023-10-14' },
              { id: 'LMX-022', src: 'TMC-2', ref: 'SELENE TC', status: 'Flagged', matches: 81, date: '2023-10-12' }
            ].map(row => (
              <tr key={row.id} className="hover:bg-[#3a506b]/20 transition-colors">
                <td className="p-4 font-mono text-[#00e5ff]">{row.id}</td>
                <td className="p-4 text-gray-300">{row.src}</td>
                <td className="p-4 text-gray-300">{row.ref}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 text-xs rounded-full ${row.status === 'Completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                    {row.status}
                  </span>
                </td>
                <td className="p-4 text-gray-300">{row.matches}</td>
                <td className="p-4 text-gray-500 text-sm">{row.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
''',
    'src/pages/NewAnalysis.tsx': '''import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload } from 'lucide-react';

export default function NewAnalysis() {
  const navigate = useNavigate();
  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [refImage, setRefImage] = useState<string | null>(null);

  const startAnalysis = () => {
    navigate('/analysis/LMX-025');
  };

  const handleUpload = (type: 'source' | 'ref') => (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      if (type === 'source') setSourceImage(url);
      else setRefImage(url);
    }
  };

  const loadDemo = () => {
    setSourceImage('/demo-data/ohrc_demo.jpg');
    setRefImage('/demo-data/lro_nac_demo.jpg');
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">New Lunar Correspondence Analysis</h1>
        <button onClick={loadDemo} className="text-sm bg-[#3a506b] px-4 py-2 rounded text-white hover:bg-[#1c2541]">
          Load Demo Analysis
        </button>
      </div>
      
      <div className="grid grid-cols-2 gap-8">
        {/* Source */}
        <div className="bg-[#1c2541] p-6 rounded-lg border border-[#3a506b]">
          <h2 className="text-xl font-semibold mb-4 text-[#00e5ff]">SOURCE IMAGE</h2>
          <div className="mb-4">
            <label className="block text-sm text-gray-400 mb-2">Sensor Profile</label>
            <select className="w-full bg-[#0a1128] border border-[#3a506b] rounded p-2 text-white">
              <option>OHRC</option>
              <option>TMC-2</option>
              <option>IIRS</option>
            </select>
          </div>
          
          <div className="border-2 border-dashed border-[#3a506b] rounded-lg h-64 flex flex-col items-center justify-center relative overflow-hidden">
            {sourceImage ? (
              <img src={sourceImage} className="w-full h-full object-cover" />
            ) : (
              <div className="text-center p-4">
                <Upload className="mx-auto text-gray-500 mb-2" size={32} />
                <p className="text-gray-400">Drag & Drop or Browse</p>
              </div>
            )}
            <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleUpload('source')} />
          </div>
        </div>

        {/* Reference */}
        <div className="bg-[#1c2541] p-6 rounded-lg border border-[#3a506b]">
          <h2 className="text-xl font-semibold mb-4 text-green-400">REFERENCE IMAGE</h2>
          <div className="mb-4">
            <label className="block text-sm text-gray-400 mb-2">Reference Sensor</label>
            <select className="w-full bg-[#0a1128] border border-[#3a506b] rounded p-2 text-white">
              <option>LRO NAC</option>
              <option>SELENE TC</option>
            </select>
          </div>
          
          <div className="border-2 border-dashed border-[#3a506b] rounded-lg h-64 flex flex-col items-center justify-center relative overflow-hidden">
            {refImage ? (
              <img src={refImage} className="w-full h-full object-cover" />
            ) : (
              <div className="text-center p-4">
                <Upload className="mx-auto text-gray-500 mb-2" size={32} />
                <p className="text-gray-400">Drag & Drop or Browse</p>
              </div>
            )}
            <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleUpload('ref')} />
          </div>
        </div>
      </div>

      <div className="mt-12 text-center">
        <button 
          onClick={startAnalysis}
          disabled={!sourceImage || !refImage}
          className="bg-[#00e5ff] text-black px-12 py-4 rounded-lg font-bold text-xl hover:bg-[#18ffff] transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(0,229,255,0.4)]"
        >
          Analyze Correspondence
        </button>
      </div>
    </div>
  );
}
''',
    'src/pages/AnalysisPipeline.tsx': '''import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, CircleDashed, Circle } from 'lucide-react';

const stages = [
  "Spatial Archive Search",
  "Ingestion & Calibration",
  "Radiometric / Spectral Normalization",
  "Physical Geometry",
  "GSD / PSF Matching",
  "Multimodal Representation",
  "Candidate Matching",
  "Geometric Verification",
  "Sub-Pixel Refinement",
  "Uncertainty Analysis"
];

export default function AnalysisPipeline() {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (currentStage >= stages.length) {
      setTimeout(() => navigate('/analysis/LMX-025/correspondence'), 1000);
      return;
    }
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          setCurrentStage(c => c + 1);
          return 0;
        }
        return p + 10;
      });
    }, 100);
    return () => clearInterval(interval);
  }, [currentStage, navigate]);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold text-white mb-2">Analysis Running</h1>
        <p className="text-gray-400">ID: LMX-025</p>
      </div>

      <div className="bg-[#1c2541] rounded-lg border border-[#3a506b] p-8 shadow-xl">
        <div className="space-y-6">
          {stages.map((stage, idx) => {
            const isCompleted = idx < currentStage;
            const isActive = idx === currentStage;
            
            return (
              <div key={stage} className={`flex items-center gap-4 ${!isCompleted && !isActive ? 'opacity-40' : ''}`}>
                <div className="w-8 flex justify-center">
                  {isCompleted ? (
                    <CheckCircle2 className="text-green-500" />
                  ) : isActive ? (
                    <CircleDashed className="text-[#00e5ff] animate-spin" />
                  ) : (
                    <Circle className="text-gray-500" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className={`font-semibold ${isActive ? 'text-[#00e5ff]' : 'text-white'}`}>
                      {String(idx + 1).padStart(2, '0')} {stage}
                    </span>
                    {isActive && <span className="text-xs text-[#00e5ff]">{progress}%</span>}
                    {isCompleted && <span className="text-xs text-green-500">100%</span>}
                  </div>
                  {isActive && (
                    <div className="h-1 bg-[#0a1128] rounded overflow-hidden">
                      <div className="h-full bg-[#00e5ff] transition-all duration-100" style={{ width: `${progress}%` }} />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
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
