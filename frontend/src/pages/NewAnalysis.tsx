import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload } from 'lucide-react';

export default function NewAnalysis() {
  const navigate = useNavigate();
  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [refImage, setRefImage] = useState<string | null>(null);

  const startAnalysis = () => {
    navigate('/analysis/latest');
  };

  const handleUpload = (type: 'source' | 'ref') => (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      if (type === 'source') setSourceImage(url);
      else setRefImage(url);
    }
  };

  const loadRealData = () => {
    setSourceImage('/real-data/ohrc_preview.png');
    setRefImage('/real-data/lro_preview.png');
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">New Lunar Correspondence Analysis</h1>
        <button onClick={loadRealData} className="text-sm bg-green-700 px-4 py-2 rounded text-white hover:bg-green-600">
          Load Real Phase 2 Data
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
