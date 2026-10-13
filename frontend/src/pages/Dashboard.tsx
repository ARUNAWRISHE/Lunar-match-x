import { Link } from 'react-router-dom';

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
