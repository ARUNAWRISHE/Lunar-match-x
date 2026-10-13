import type { ReactNode } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Starfield from './components/Starfield';
import Landing from './pages/Landing';
import Workspace from './pages/Workspace';
import Architecture from './pages/Architecture';
import Status from './pages/Status';

function MissionLayout({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex h-screen bg-[#03040a] text-white font-sans overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_60%_at_15%_0%,rgba(58,80,107,0.3),transparent_55%),radial-gradient(ellipse_70%_50%_at_100%_100%,rgba(0,229,255,0.06),transparent_55%)]" />
      <Starfield count={220} className="opacity-90" />
      <Sidebar />
      <main className="relative z-10 flex-1 overflow-y-auto scroll-smooth">{children}</main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/workspace" element={<MissionLayout><Workspace /></MissionLayout>} />
        <Route path="/architecture" element={<MissionLayout><Architecture /></MissionLayout>} />
        <Route path="/status" element={<MissionLayout><Status /></MissionLayout>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
