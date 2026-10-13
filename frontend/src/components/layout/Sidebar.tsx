import { NavLink, Link } from 'react-router-dom';
import { LayoutDashboard, Network, ListChecks, Activity, Orbit } from 'lucide-react';

const Sidebar = () => {
  const links = [
    { to: '/workspace', label: 'Mission Workspace', icon: LayoutDashboard },
    { to: '/architecture', label: 'Architecture', icon: Network },
    { to: '/status', label: 'Implementation Status', icon: ListChecks },
  ];

  return (
    <div className="relative z-10 w-64 bg-[#0d1326]/60 backdrop-blur-md border-r border-[#3a506b]/60 flex flex-col justify-between shrink-0">
      <div>
        <Link to="/" className="block p-6 hover:bg-[#3a506b]/20 transition-colors">
          <div className="flex items-center gap-2 text-[#00e5ff]">
            <Orbit size={18} />
            <h1 className="font-display text-xl font-bold tracking-wider">LUNARMATCH-X</h1>
          </div>
          <p className="text-[10px] text-gray-400 mt-1 uppercase tracking-widest leading-tight">Unified Physics-Aware Lunar Correspondence Pipeline</p>
        </Link>
        <nav className="mt-6 flex flex-col gap-1 px-4">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${
                  isActive ? 'bg-[#3a506b] text-white' : 'text-gray-400 hover:bg-[#3a506b]/50 hover:text-gray-200'
                }`
              }
            >
              <link.icon size={20} />
              <span>{link.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
      
      <div className="p-6 border-t border-[#3a506b]">
        <div className="flex items-center gap-2 mb-2">
          <Activity size={16} className="text-[#00e5ff]" />
          <span className="text-sm text-gray-300">System Status</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-green-500 font-semibold tracking-wider">PIPELINE READY</span>
        </div>
        <div className="mt-4 px-3 py-1 bg-[#3a506b]/30 text-gray-300 border border-[#3a506b] rounded-md text-xs font-bold text-center">
          "Visual correspondence proposes. Physics verifies. Uncertainty decides."
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
