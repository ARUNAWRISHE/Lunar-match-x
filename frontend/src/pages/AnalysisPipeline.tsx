import { useState, useEffect } from 'react';
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
      setTimeout(() => navigate('/analysis/latest/correspondence'), 1000);
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
