import { useMemo } from 'react';

interface StarfieldProps {
  count?: number;
  className?: string;
  shootingStars?: boolean;
  seed?: number;
}

function mulberry32(seed: number) {
  let a = seed;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Lightweight CSS-only starfield background — deterministic per mount, no canvas. */
export default function Starfield({ count = 140, className = '', shootingStars = true, seed = 1337 }: StarfieldProps) {
  const stars = useMemo(() => {
    const rand = mulberry32(seed);
    return Array.from({ length: count }, (_, i) => {
      const r = rand();
      const size = r < 0.78 ? 1 : r < 0.94 ? 1.7 : 2.6;
      return {
        id: i,
        top: rand() * 100,
        left: rand() * 100,
        size,
        opacity: 0.3 + rand() * 0.65,
        duration: 2 + rand() * 4,
        delay: rand() * 6,
      };
    });
  }, [count, seed]);

  const streaks = useMemo(() => {
    if (!shootingStars) return [];
    const rand = mulberry32(seed + 777);
    return Array.from({ length: 4 }, (_, i) => ({
      id: i,
      top: rand() * 55,
      left: 10 + rand() * 70,
      length: 90 + rand() * 70,
      duration: 5 + rand() * 3,
      delay: rand() * 20 + i * 6,
    }));
  }, [shootingStars, seed]);

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`} aria-hidden="true">
      {stars.map((s) => (
        <div
          key={s.id}
          className="absolute rounded-full bg-white"
          style={{
            top: `${s.top}%`,
            left: `${s.left}%`,
            width: s.size,
            height: s.size,
            ['--tw-star-opacity' as string]: s.opacity,
            opacity: s.opacity,
            animation: `twinkle ${s.duration}s ease-in-out ${s.delay}s infinite`,
            boxShadow: s.size > 1.8 ? '0 0 5px 1px rgba(255,255,255,0.85)' : undefined,
          }}
        />
      ))}
      {streaks.map((s) => (
        <div
          key={`streak-${s.id}`}
          className="absolute"
          style={{
            top: `${s.top}%`,
            left: `${s.left}%`,
            width: s.length,
            height: 2,
            background: 'linear-gradient(90deg, rgba(255,255,255,0.9), rgba(255,255,255,0))',
            borderRadius: 2,
            transform: 'rotate(-32deg)',
            animation: `shooting-star ${s.duration}s linear ${s.delay}s infinite`,
            opacity: 0,
          }}
        />
      ))}
    </div>
  );
}
