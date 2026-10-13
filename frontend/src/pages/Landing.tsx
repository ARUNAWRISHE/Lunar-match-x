import { useNavigate } from 'react-router-dom';
import { ArrowUpRight, Satellite, Radar, Orbit } from 'lucide-react';
import Starfield from '../components/Starfield';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="relative w-full h-full min-h-screen overflow-hidden bg-[#05070f] text-white">
      {/* ── Background layers ─────────────────────────────────────── */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_30%_20%,rgba(58,80,107,0.35),transparent_60%),radial-gradient(ellipse_100%_60%_at_80%_90%,rgba(0,229,255,0.06),transparent_55%)]" />
      <Starfield count={160} />

      {/* Orbit arc */}
      <svg className="absolute top-0 left-0 w-full h-[340px] opacity-70" viewBox="0 0 1200 340" preserveAspectRatio="none" aria-hidden="true">
        <path d="M -50 260 Q 500 40 1250 120" stroke="rgba(255,255,255,0.18)" strokeWidth="1" fill="none" />
        <circle cx="990" cy="128" r="5" fill="#e8a86c">
          <animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite" />
        </circle>
      </svg>

      {/* ── Moon — real lunar photograph, bleeding off the left edge ── */}
      <div className="absolute -left-[140px] top-1/2 -translate-y-1/2 w-[720px] h-[720px] pointer-events-none">
        {/* ambient glow behind the disc */}
        <div className="absolute inset-[8%] rounded-full" style={{ boxShadow: '0 0 180px 50px rgba(232,168,108,0.10)' }} />
        <img
          src="/moon.png"
          alt=""
          className="absolute inset-0 w-full h-full object-contain"
          style={{ filter: 'drop-shadow(0 0 70px rgba(200,210,230,0.15))' }}
        />
      </div>

      {/* ── Foreground content ────────────────────────────────────── */}
      <div className="relative z-10 flex flex-col min-h-screen px-8 md:px-16">

        {/* Top bar */}
        <header className="flex items-center justify-between pt-8">
          <div className="flex items-center gap-2.5">
            <Orbit size={20} className="text-[#00e5ff]" />
            <span className="font-display font-semibold tracking-[0.2em] text-sm">LUNARMATCH·X</span>
          </div>
          <span className="hidden sm:block text-[10px] tracking-[0.25em] text-gray-500 font-mono-sf">SIH 2026 · PS 26166</span>
        </header>

        {/* Middle — headline */}
        <main className="flex-1 flex flex-col justify-center max-w-3xl ml-auto text-right mt-10">
          <p className="text-[11px] tracking-[0.3em] text-[#00e5ff] font-mono-sf mb-3">
            OHRC × LRO NAC CORRESPONDENCE ENGINE
          </p>
          <h1 className="font-display font-bold leading-[0.95] text-[64px] md:text-[104px] text-white">
            LunarMatch<span className="text-[#e8a86c]">-X.</span>
          </h1>
          <p className="mt-6 text-gray-400 text-sm md:text-base leading-relaxed max-w-md ml-auto">
            Automated correspondence between Chandrayaan-2 OHRC (0.25&nbsp;m/px) and LRO NAC (1.2&nbsp;m/px)
            imagery. Visual correspondence proposes. Physics verifies. Uncertainty decides.
          </p>

          <div className="flex items-center justify-end gap-4 mt-9">
            <button
              onClick={() => navigate('/workspace')}
              className="group flex items-center gap-2.5 pl-6 pr-5 py-3 bg-[#00e5ff] text-black font-semibold text-sm rounded-full hover:bg-[#18ffff] transition-colors shadow-[0_0_30px_rgba(0,229,255,0.25)]"
            >
              Launch Mission Workspace
              <ArrowUpRight size={17} className="transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </button>
          </div>
        </main>

        {/* Bottom row */}
        <footer className="flex items-end justify-end pb-10">
          <div className="flex items-center gap-6 text-gray-500">
            <div className="flex items-center gap-1.5 text-xs">
              <Satellite size={14} className="text-[#00e5ff]" /> ISRO&nbsp;OHRC
            </div>
            <div className="flex items-center gap-1.5 text-xs">
              <Radar size={14} className="text-[#00e5ff]" /> NASA&nbsp;LRO&nbsp;NAC
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
