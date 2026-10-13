import { useState } from 'react';
import { ZoomIn, X } from 'lucide-react';

const PRODUCTS = [
  {
    key: 'registered',
    label: 'Registered Image',
    src: '/outputs/registered_image.png',
    status: 'REAL',
    statusColor: 'text-green-400 border-green-500/50 bg-green-500/10',
    caption: 'False-colour OHRC↔LRO blend (real data)',
  },
  {
    key: 'tiepoints',
    label: 'Matched Tie-Points',
    src: '/outputs/matched_tiepoints.png',
    status: 'REAL',
    statusColor: 'text-green-400 border-green-500/50 bg-green-500/10',
    caption: '4 RANSAC inliers from Phase 2.2',
  },
  {
    key: 'dem',
    label: 'DEM / Terrain Product',
    src: '/outputs/dem_product.png',
    status: 'SIMULATED',
    statusColor: 'text-yellow-400 border-yellow-500/50 bg-yellow-500/10',
    caption: 'Synthetic terrain proxy (SPICE/DEM planned)',
  },
  {
    key: 'footprints',
    label: 'Footprints & Metadata',
    src: '/outputs/footprints_metadata.png',
    status: 'REAL',
    statusColor: 'text-green-400 border-green-500/50 bg-green-500/10',
    caption: 'OHRC ∩ M176219771RE overlap polygon',
  },
  {
    key: 'uncertainty',
    label: 'Uncertainty / Validity Map',
    src: '/outputs/uncertainty_map.png',
    status: 'PARTIAL',
    statusColor: 'text-amber-400 border-amber-500/50 bg-amber-500/10',
    caption: 'Spatial confidence field (JET colormap)',
    wideCaption: (
      <div className="mt-2 flex flex-col items-end gap-0.5 text-[10px]">
        <span className="text-red-400 font-bold">▬ High Uncertainty</span>
        <span className="text-yellow-400">▬ Medium</span>
        <span className="text-blue-400 font-bold">▬ Low Uncertainty</span>
      </div>
    ),
  },
];

export default function GeneratedImages({ show }: { show: boolean }) {
  const [lightbox, setLightbox] = useState<typeof PRODUCTS[0] | null>(null);

  if (!show) return null;

  return (
    <>
      {/* LIGHTBOX */}
      {lightbox && (
        <div
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-8"
          onClick={() => setLightbox(null)}
        >
          <div className="relative max-w-5xl w-full bg-[#0a1128] border border-[#3a506b] rounded-xl p-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <button className="absolute top-3 right-3 text-gray-400 hover:text-white" onClick={() => setLightbox(null)}>
              <X size={20} />
            </button>
            <p className="text-sm text-gray-400 mb-3 font-mono">{lightbox.label}</p>
            <img src={lightbox.src} className="w-full max-h-[70vh] object-contain rounded" />
            <p className="text-xs text-gray-500 mt-2">{lightbox.caption}</p>
          </div>
        </div>
      )}

      <div className="bg-[#1c2541] border border-[#3a506b] rounded-xl p-6 mt-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-1 h-8 bg-[#00e5ff] rounded-full" />
          <div>
            <h2 className="text-xl font-bold text-white tracking-wide">Generated Images</h2>
            <p className="text-xs text-gray-400 mt-0.5">Pipeline output products — Phase 2.2 results</p>
          </div>
        </div>

        {/* Grid: first row 3, second row 2 centred */}
        <div className="flex flex-col gap-4">
          {/* Row 1 */}
          <div className="grid grid-cols-3 gap-4">
            {PRODUCTS.slice(0, 3).map(p => (
              <ProductCard key={p.key} product={p} onZoom={() => setLightbox(p)} />
            ))}
          </div>
          {/* Row 2 — centred */}
          <div className="flex justify-center gap-4">
            {PRODUCTS.slice(3).map(p => (
              <div key={p.key} className="w-[calc(33.333%-8px)]">
                <ProductCard product={p} onZoom={() => setLightbox(p)} />
              </div>
            ))}
          </div>
        </div>

        {/* Footer quote */}
        <div className="mt-6 border-t border-[#3a506b] pt-4 text-center">
          <p className="text-xs text-gray-500 italic">
            "LunarMatch-X does not assume every visual match is correct.{' '}
            <span className="text-gray-400">Visual correspondence proposes. Physics verifies. Uncertainty decides.</span>"
          </p>
        </div>
      </div>
    </>
  );
}

function ProductCard({
  product,
  onZoom,
}: {
  product: typeof PRODUCTS[0];
  onZoom: () => void;
}) {
  return (
    <div className="group bg-[#0a1128] border border-[#3a506b] rounded-lg overflow-hidden hover:border-[#00e5ff] transition-colors cursor-pointer" onClick={onZoom}>
      {/* Image */}
      <div className="relative h-44 bg-black flex items-center justify-center overflow-hidden">
        <img
          src={product.src}
          alt={product.label}
          className="w-full h-full object-cover opacity-85 group-hover:opacity-100 transition-opacity group-hover:scale-105 duration-300"
        />
        {/* Zoom icon on hover */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/30">
          <ZoomIn size={32} className="text-white" />
        </div>
        {/* Status badge */}
        <span className={`absolute top-2 right-2 text-[10px] font-bold px-2 py-0.5 rounded border ${product.statusColor}`}>
          {product.status}
        </span>
      </div>

      {/* Label */}
      <div className="p-3">
        <p className="text-sm font-semibold text-white leading-tight">{product.label}</p>
        <p className="text-[11px] text-gray-500 mt-1">{product.caption}</p>
        {'wideCaption' in product && product.wideCaption}
      </div>
    </div>
  );
}
