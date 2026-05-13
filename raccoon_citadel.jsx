import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy, Scale, Shield, AlertTriangle,
  BookOpen, Lock, Eye, Leaf, X, ChevronRight,
  Activity, TrendingUp, Zap, Archive
} from "lucide-react";

// ─── Sample Data ────────────────────────────────────────────────────────────

const SAMPLE_DATA = {
  champion_gate: {
    title: "Champion Gate",
    subtitle: "Promotion Eligibility Council",
    stats: [
      { label: "Candidates Today", value: "3" },
      { label: "Promoted This Week", value: "1" },
      { label: "Collision Blocks", value: "2" },
      { label: "Gate Threshold", value: "0.72" },
    ],
    log: [
      "[DAY 47] Bold_Cautious_v2 — PROMOTED to CHAMPION",
      "[DAY 45] Reckless_Firecracker — BLOCKED: collision_warning active",
      "[DAY 44] Careful_Garden — ELIGIBLE: awaiting review window",
      "[DAY 43] Stone_Raccoon — INELIGIBLE: inertness threshold reached",
      "[DAY 40] Chaos_Snack — TRIAL extended: insufficient clean streak",
    ],
    accent: "amber",
  },
  collision_court: {
    title: "Collision Court",
    subtitle: "Strategy Overlap Diagnostics",
    stats: [
      { label: "Active Warnings", value: "2" },
      { label: "Resolved Today", value: "1" },
      { label: "Avg Similarity", value: "0.61" },
      { label: "Court Sessions", value: "14" },
    ],
    log: [
      "[DAY 47] Bold_Cautious_v2 × Stone_Raccoon — similarity 0.71 — WARNING",
      "[DAY 47] Chaos_Snack × Careful_Garden — similarity 0.43 — CLEAR",
      "[DAY 46] Reckless_Firecracker × Chaos_Snack — similarity 0.88 — BLOCK",
      "[DAY 45] Stone_Raccoon × Careful_Garden — similarity 0.39 — CLEAR",
      "[DAY 44] Bold_Cautious_v2 × Careful_Garden — similarity 0.52 — WATCH",
    ],
    accent: "violet",
  },
  door_guard: {
    title: "Door Guard",
    subtitle: "Audit vs Live Mode Sentinel",
    stats: [
      { label: "Mode", value: "AUDIT" },
      { label: "Signals Screened", value: "219" },
      { label: "Live Blocks", value: "0" },
      { label: "Lookahead Flags", value: "7" },
    ],
    log: [
      "[DAY 47] AUDIT — next-bar data permitted for Bold_Cautious_v2",
      "[DAY 47] LIVE check — Careful_Garden: WATCH_RETURN label applied",
      "[DAY 46] AUDIT — lookahead confirmed for storm_false_followthrough era",
      "[DAY 45] LIVE check — Chaos_Snack: signal valid, no lookahead detected",
      "[DAY 44] Mode: switched to AUDIT for backtest session #14",
    ],
    accent: "cyan",
  },
  risk_governor: {
    title: "Risk Governor",
    subtitle: "Exposure Caps & Authority Limits",
    stats: [
      { label: "Max Authority", value: "0.85" },
      { label: "Overrides Today", value: "0" },
      { label: "Capped Entries", value: "3" },
      { label: "Risk Score Avg", value: "0.44" },
    ],
    log: [
      "[DAY 47] Bold_Cautious_v2 — authority 0.82 — WITHIN CAP",
      "[DAY 47] Reckless_Firecracker — authority 0.91 — CAPPED to 0.85",
      "[DAY 46] Chaos_Snack — authority 0.67 — WITHIN CAP",
      "[DAY 45] Stone_Raccoon — authority 0.41 — WITHIN CAP",
      "[DAY 44] Careful_Garden — authority 0.78 — WITHIN CAP",
    ],
    accent: "orange",
  },
  wisdom_archive: {
    title: "Wisdom Archive",
    subtitle: "Scored Memory Ledger",
    stats: [
      { label: "Total Memories", value: "847" },
      { label: "Active", value: "312" },
      { label: "Quarantined", value: "41" },
      { label: "Avg Wisdom Score", value: "0.63" },
    ],
    log: [
      "[DAY 47] Memory #0412 — score 0.79 — ACTIVE — Bold_Cautious_v2",
      "[DAY 47] Memory #0388 — score 0.31 — QUARANTINE — contamination 0.71",
      "[DAY 46] Memory #0401 — score 0.55 — REACTIVATION_TRIAL",
      "[DAY 46] Memory #0377 — score 0.68 — ACTIVE — Careful_Garden",
      "[DAY 45] Memory #0349 — score 0.21 — PROBATION — staleness 0.88",
    ],
    accent: "emerald",
  },
  quarantine_wing: {
    title: "Quarantine Wing",
    subtitle: "Isolation & Rehabilitation",
    stats: [
      { label: "Quarantined", value: "41" },
      { label: "In Rehab Trial", value: "8" },
      { label: "Clean Streak Avg", value: "1.4" },
      { label: "Released Today", value: "2" },
    ],
    log: [
      "[DAY 47] Memory #0388 — entered QUARANTINE — contamination 0.71",
      "[DAY 47] Memory #0291 — REHAB_TRIAL day 3 — streak 2 — clean",
      "[DAY 47] Memory #0317 — promoted LIGHT — rehab successful",
      "[DAY 46] Memory #0355 — REHAB_TRIAL day 1 — contamination 0.28",
      "[DAY 45] Memory #0302 — released from quarantine — contamination clear",
    ],
    accent: "rose",
  },
  observatory: {
    title: "Market Weather Observatory",
    subtitle: "Two-Axis Weather Classification",
    stats: [
      { label: "Current Weather", value: "LOUD_VIOLENT" },
      { label: "Session Streak", value: "3 days" },
      { label: "Calm Windows", value: "12" },
      { label: "Storm Events", value: "4" },
    ],
    log: [
      "[DAY 47] LOUD_VOLUME × VIOLENT_PRICE → LOUD_VIOLENT — storm active",
      "[DAY 46] LOUD_VOLUME × VIOLENT_PRICE → LOUD_VIOLENT — storm continues",
      "[DAY 45] CALM_VOLUME × VIOLENT_PRICE → CALM_VIOLENT — transitional",
      "[DAY 44] LOUD_VOLUME × CALM_PRICE → LOUD_CALM — volume spike, no follow",
      "[DAY 43] CALM_VOLUME × CALM_PRICE → CALM_CALM — baseline session",
    ],
    accent: "sky",
  },
  strategy_nursery: {
    title: "Strategy Nursery",
    subtitle: "Creature Onboarding & Lane Assignment",
    stats: [
      { label: "Nursery Residents", value: "2" },
      { label: "Graduated Today", value: "1" },
      { label: "Lane Conflicts", value: "0" },
      { label: "Avg Incubation", value: "6.2 days" },
    ],
    log: [
      "[DAY 47] Ghost_Riser_v1 — entered nursery — lane: calm_volatile_reversal",
      "[DAY 47] Drift_Ember — day 4 incubation — lane check: clear",
      "[DAY 46] Momentum_Sneak — graduated nursery → ACTIVE_TRIAL",
      "[DAY 45] Ghost_Riser_v1 — lane assignment: storm_false_followthrough",
      "[DAY 44] Drift_Ember — entered nursery — lane: loud_calm_continuation",
    ],
    accent: "lime",
  },
};

const ROOMS = [
  { id: "champion_gate",   label: "Champion Gate",   Icon: Trophy,        x: 50, y: 9,  accent: "amber"   },
  { id: "collision_court", label: "Collision Court", Icon: Scale,         x: 14, y: 26, accent: "violet"  },
  { id: "door_guard",      label: "Door Guard",      Icon: Shield,        x: 86, y: 26, accent: "cyan"    },
  { id: "risk_governor",   label: "Risk Governor",   Icon: AlertTriangle, x: 7,  y: 52, accent: "orange"  },
  { id: "wisdom_archive",  label: "Wisdom Archive",  Icon: BookOpen,      x: 93, y: 52, accent: "emerald" },
  { id: "quarantine_wing", label: "Quarantine Wing", Icon: Lock,          x: 14, y: 78, accent: "rose"    },
  { id: "observatory",     label: "Observatory",     Icon: Eye,           x: 86, y: 78, accent: "sky"     },
  { id: "strategy_nursery",label: "Strategy Nursery",Icon: Leaf,          x: 50, y: 91, accent: "lime"    },
];

const CREATURES = [
  { id: "bold",    label: "Bold_Cautious_v2",     status: "CHAMPION",      color: "#f59e0b", x: 38, y: 38, emoji: "🦝" },
  { id: "careful", label: "Careful_Garden",        status: "ACTIVE",        color: "#10b981", x: 56, y: 42, emoji: "🌱" },
  { id: "chaos",   label: "Chaos_Snack",           status: "ACTIVE_TRIAL",  color: "#8b5cf6", x: 45, y: 58, emoji: "⚡" },
  { id: "stone",   label: "Stone_Raccoon",          status: "BASELINE",      color: "#64748b", x: 60, y: 55, emoji: "🪨" },
  { id: "reckless",label: "Reckless_Firecracker",  status: "QUARANTINED",   color: "#f43f5e", x: 40, y: 62, emoji: "🔒" },
];

const ACCENT_CLASSES = {
  amber:   { border: "border-amber-500",   text: "text-amber-400",   bg: "bg-amber-500/10",   glow: "#f59e0b", dot: "bg-amber-500"   },
  violet:  { border: "border-violet-500",  text: "text-violet-400",  bg: "bg-violet-500/10",  glow: "#8b5cf6", dot: "bg-violet-500"  },
  cyan:    { border: "border-cyan-500",    text: "text-cyan-400",    bg: "bg-cyan-500/10",    glow: "#06b6d4", dot: "bg-cyan-500"    },
  orange:  { border: "border-orange-500",  text: "text-orange-400",  bg: "bg-orange-500/10",  glow: "#f97316", dot: "bg-orange-500"  },
  emerald: { border: "border-emerald-500", text: "text-emerald-400", bg: "bg-emerald-500/10", glow: "#10b981", dot: "bg-emerald-500" },
  rose:    { border: "border-rose-500",    text: "text-rose-400",    bg: "bg-rose-500/10",    glow: "#f43f5e", dot: "bg-rose-500"    },
  sky:     { border: "border-sky-500",     text: "text-sky-400",     bg: "bg-sky-500/10",     glow: "#0ea5e9", dot: "bg-sky-500"     },
  lime:    { border: "border-lime-500",    text: "text-lime-400",    bg: "bg-lime-500/10",    glow: "#84cc16", dot: "bg-lime-500"    },
};

// ─── Hex Glyph Corner Decoration ────────────────────────────────────────────

function HexGlyph({ color = "#334155", size = 40 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <polygon
        points="20,2 36,11 36,29 20,38 4,29 4,11"
        stroke={color} strokeWidth="1.2" fill="none" opacity="0.6"
      />
      <polygon
        points="20,8 31,14 31,26 20,32 9,26 9,14"
        stroke={color} strokeWidth="0.7" fill="none" opacity="0.35"
      />
      <circle cx="20" cy="20" r="3" fill={color} opacity="0.5" />
    </svg>
  );
}

// ─── Sophon Gavel Orb ────────────────────────────────────────────────────────

function SophonOrb() {
  return (
    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none z-10">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
        className="relative w-24 h-24"
      >
        {/* Outer ring */}
        <div className="absolute inset-0 rounded-full border border-indigo-500/40" />
        {/* Orbiting dot 1 */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
          className="absolute inset-2"
        >
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-indigo-400 shadow-[0_0_6px_#818cf8]" />
        </motion.div>
        {/* Orbiting dot 2 */}
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 9, repeat: Infinity, ease: "linear" }}
          className="absolute inset-4"
        >
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-violet-400 shadow-[0_0_4px_#a78bfa]" />
        </motion.div>
      </motion.div>

      {/* Core orb */}
      <motion.div
        animate={{ scale: [1, 1.08, 1], opacity: [0.85, 1, 0.85] }}
        transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700 shadow-[0_0_24px_#6366f1,0_0_8px_#a78bfa] flex items-center justify-center"
      >
        <span className="text-white text-xs font-bold tracking-widest select-none">S</span>
      </motion.div>

      {/* Label */}
      <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-xs text-indigo-400 font-mono tracking-widest opacity-70">
        SOPHON
      </div>
    </div>
  );
}

// ─── Animated Creature ───────────────────────────────────────────────────────

function Creature({ creature, mapRef }) {
  const [pos, setPos] = useState({ x: creature.x, y: creature.y });
  const targetRef = useRef({ x: creature.x, y: creature.y });
  const frameRef = useRef(null);

  useEffect(() => {
    if (creature.status === "QUARANTINED") return;

    const wander = () => {
      targetRef.current = {
        x: creature.x + (Math.random() - 0.5) * 12,
        y: creature.y + (Math.random() - 0.5) * 12,
      };
    };

    wander();
    const interval = setInterval(wander, 3000 + Math.random() * 2000);
    return () => clearInterval(interval);
  }, [creature]);

  useEffect(() => {
    if (creature.status === "QUARANTINED") return;

    const animate = () => {
      setPos(prev => ({
        x: prev.x + (targetRef.current.x - prev.x) * 0.03,
        y: prev.y + (targetRef.current.y - prev.y) * 0.03,
      }));
      frameRef.current = requestAnimationFrame(animate);
    };
    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [creature.status]);

  return (
    <motion.div
      className="absolute pointer-events-none select-none"
      style={{ left: `${pos.x}%`, top: `${pos.y}%`, transform: "translate(-50%,-50%)" }}
      animate={creature.status === "QUARANTINED" ? { opacity: [0.4, 0.7, 0.4] } : {}}
      transition={creature.status === "QUARANTINED" ? { duration: 2, repeat: Infinity } : {}}
    >
      <div className="flex flex-col items-center gap-0.5">
        <div className="text-base leading-none" title={`${creature.label} — ${creature.status}`}>
          {creature.emoji}
        </div>
        <div
          className="text-[8px] font-mono font-bold px-1 rounded leading-none"
          style={{ color: creature.color, textShadow: `0 0 6px ${creature.color}` }}
        >
          {creature.id.toUpperCase()}
        </div>
      </div>
    </motion.div>
  );
}

// ─── Room Node ───────────────────────────────────────────────────────────────

function RoomNode({ room, isActive, onClick }) {
  const ac = ACCENT_CLASSES[room.accent];
  const { Icon } = room;

  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.12 }}
      whileTap={{ scale: 0.95 }}
      className="absolute flex flex-col items-center gap-1 cursor-pointer group"
      style={{ left: `${room.x}%`, top: `${room.y}%`, transform: "translate(-50%,-50%)" }}
    >
      {/* Room icon container */}
      <motion.div
        animate={isActive ? { boxShadow: [`0 0 12px ${ac.glow}`, `0 0 28px ${ac.glow}`, `0 0 12px ${ac.glow}`] } : {}}
        transition={{ duration: 1.6, repeat: Infinity }}
        className={`
          w-11 h-11 rounded-lg border-2 flex items-center justify-center
          bg-slate-900/90 backdrop-blur transition-all duration-200
          ${isActive ? `${ac.border} ${ac.bg}` : "border-slate-700 group-hover:" + ac.border}
        `}
        style={isActive ? { boxShadow: `0 0 18px ${ac.glow}60` } : {}}
      >
        <Icon
          size={20}
          className={isActive ? ac.text : "text-slate-400 group-hover:" + ac.text.replace("text-", "text-")}
          style={isActive ? { filter: `drop-shadow(0 0 4px ${ac.glow})` } : {}}
        />
      </motion.div>

      {/* Room label */}
      <span
        className={`
          text-[9px] font-mono font-semibold tracking-wide whitespace-nowrap
          transition-colors duration-150
          ${isActive ? ac.text : "text-slate-500 group-hover:text-slate-300"}
        `}
      >
        {room.label.toUpperCase()}
      </span>

      {/* Active indicator dot */}
      {isActive && (
        <motion.div
          layoutId="active-dot"
          className={`w-1.5 h-1.5 rounded-full ${ac.dot}`}
          style={{ boxShadow: `0 0 6px ${ac.glow}` }}
        />
      )}
    </motion.button>
  );
}

// ─── Side Panel ──────────────────────────────────────────────────────────────

function SidePanel({ roomId, onClose }) {
  const data = SAMPLE_DATA[roomId];
  if (!data) return null;
  const ac = ACCENT_CLASSES[data.accent];

  return (
    <motion.div
      initial={{ x: 340, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 340, opacity: 0 }}
      transition={{ type: "spring", stiffness: 280, damping: 30 }}
      className={`
        absolute right-0 top-0 h-full w-80 z-30
        bg-slate-950/95 backdrop-blur border-l-2 ${ac.border}
        flex flex-col overflow-hidden
      `}
      style={{ boxShadow: `-8px 0 32px ${ac.glow}20` }}
    >
      {/* Panel header */}
      <div className={`flex items-start justify-between p-4 border-b border-slate-800 ${ac.bg}`}>
        <div>
          <h2 className={`text-sm font-bold font-mono tracking-wide ${ac.text}`}>
            {data.title.toUpperCase()}
          </h2>
          <p className="text-[10px] text-slate-500 mt-0.5 font-mono">{data.subtitle}</p>
        </div>
        <button
          onClick={onClose}
          className="text-slate-600 hover:text-slate-300 transition-colors mt-0.5"
        >
          <X size={16} />
        </button>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-2 p-4 border-b border-slate-800">
        {data.stats.map((stat) => (
          <div key={stat.label} className={`rounded p-2 ${ac.bg} border border-slate-800`}>
            <div className={`text-base font-bold font-mono ${ac.text}`}>{stat.value}</div>
            <div className="text-[9px] text-slate-500 font-mono mt-0.5">{stat.label.toUpperCase()}</div>
          </div>
        ))}
      </div>

      {/* Log feed */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className={`text-[9px] font-mono font-semibold ${ac.text} mb-2 tracking-widest flex items-center gap-1`}>
          <Activity size={10} />
          ACTIVITY LOG
        </div>
        <div className="flex flex-col gap-2">
          {data.log.map((entry, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`text-[10px] font-mono text-slate-400 leading-snug p-2 rounded border border-slate-800 bg-slate-900/60`}
            >
              {entry}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Panel footer */}
      <div className="p-3 border-t border-slate-800 flex items-center justify-between">
        <span className="text-[9px] text-slate-600 font-mono">SAMPLE DATA · v0.1</span>
        <div className="flex items-center gap-1">
          <div className={`w-1.5 h-1.5 rounded-full ${ac.dot} animate-pulse`} />
          <span className={`text-[9px] font-mono ${ac.text}`}>LIVE</span>
        </div>
      </div>
    </motion.div>
  );
}

// ─── SVG Corridors ───────────────────────────────────────────────────────────

function Corridors({ activeRoom }) {
  const activeId = activeRoom;
  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ zIndex: 1 }}
    >
      <defs>
        <filter id="glow-line" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="0.8" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      {ROOMS.map((room) => {
        const isActive = room.id === activeId;
        const ac = ACCENT_CLASSES[room.accent];
        return (
          <line
            key={room.id}
            x1={room.x} y1={room.y}
            x2={50} y2={50}
            stroke={isActive ? ac.glow : "#1e293b"}
            strokeWidth={isActive ? "0.6" : "0.35"}
            strokeDasharray={isActive ? "none" : "1.5,1.5"}
            filter={isActive ? "url(#glow-line)" : "none"}
            opacity={isActive ? 0.9 : 0.5}
          />
        );
      })}
    </svg>
  );
}

// ─── Grid Overlay ────────────────────────────────────────────────────────────

function GridOverlay() {
  return (
    <div
      className="absolute inset-0 pointer-events-none opacity-[0.04]"
      style={{
        backgroundImage:
          "linear-gradient(#94a3b8 1px, transparent 1px), linear-gradient(90deg, #94a3b8 1px, transparent 1px)",
        backgroundSize: "5% 5%",
      }}
    />
  );
}

// ─── Corner Glyphs ───────────────────────────────────────────────────────────

function CornerGlyphs() {
  return (
    <>
      <div className="absolute top-3 left-3 opacity-30"><HexGlyph color="#6366f1" size={32} /></div>
      <div className="absolute top-3 right-3 opacity-30"><HexGlyph color="#6366f1" size={32} /></div>
      <div className="absolute bottom-3 left-3 opacity-30"><HexGlyph color="#6366f1" size={32} /></div>
      <div className="absolute bottom-3 right-3 opacity-30"><HexGlyph color="#6366f1" size={32} /></div>
    </>
  );
}

// ─── Header Bar ──────────────────────────────────────────────────────────────

function HeaderBar({ activeRoom }) {
  return (
    <div className="flex items-center justify-between px-5 py-3 border-b border-slate-800 bg-slate-950/80 backdrop-blur z-20 relative">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_8px_#6366f1] animate-pulse" />
        <span className="text-xs font-mono font-bold text-slate-300 tracking-widest">
          RACCOON QUANT CITADEL
        </span>
        <span className="text-[9px] font-mono text-slate-600">v0.1</span>
      </div>
      <div className="flex items-center gap-4 text-[9px] font-mono text-slate-500">
        <span className="flex items-center gap-1">
          <TrendingUp size={9} />
          DAY 47
        </span>
        <span className="flex items-center gap-1">
          <Zap size={9} className="text-amber-500" />
          LOUD_VIOLENT
        </span>
        <span className="flex items-center gap-1">
          <Archive size={9} />
          AUDIT MODE
        </span>
        {activeRoom && (
          <span className="flex items-center gap-1 text-indigo-400">
            <ChevronRight size={9} />
            {activeRoom.replace("_", " ").toUpperCase()}
          </span>
        )}
      </div>
    </div>
  );
}

// ─── Creature Legend ─────────────────────────────────────────────────────────

function CreatureLegend() {
  return (
    <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 flex gap-2 bg-slate-950/80 backdrop-blur border border-slate-800 rounded px-3 py-1.5">
      {CREATURES.map((c) => (
        <div key={c.id} className="flex items-center gap-1" title={`${c.label} — ${c.status}`}>
          <span className="text-[10px]">{c.emoji}</span>
          <div
            className="w-1 h-1 rounded-full"
            style={{ background: c.color, boxShadow: `0 0 4px ${c.color}` }}
          />
        </div>
      ))}
      <span className="text-[8px] text-slate-600 font-mono ml-1 self-center">COUNCIL</span>
    </div>
  );
}

// ─── Main Citadel Component ──────────────────────────────────────────────────

export default function RaccoonCitadel() {
  const [activeRoom, setActiveRoom] = useState(null);
  const mapRef = useRef(null);

  const handleRoomClick = (roomId) => {
    setActiveRoom(prev => (prev === roomId ? null : roomId));
  };

  return (
    <div className="w-full h-screen flex flex-col bg-slate-950 text-slate-100 font-mono overflow-hidden">
      <HeaderBar activeRoom={activeRoom} />

      {/* Map container */}
      <div className="flex-1 relative overflow-hidden">

        {/* Radial background gradient */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse 70% 60% at 50% 50%, #0f172a 0%, #020617 100%)",
          }}
        />

        <GridOverlay />
        <CornerGlyphs />

        {/* Stone texture ring suggestion */}
        <div
          className="absolute inset-8 rounded-full border border-slate-800/40 pointer-events-none"
          style={{ boxShadow: "inset 0 0 60px #0f172a80" }}
        />
        <div className="absolute inset-16 rounded-full border border-slate-800/20 pointer-events-none" />

        {/* Corridors */}
        <Corridors activeRoom={activeRoom} />

        {/* Sophon orb center */}
        <SophonOrb />

        {/* Rooms */}
        {ROOMS.map((room) => (
          <RoomNode
            key={room.id}
            room={room}
            isActive={activeRoom === room.id}
            onClick={() => handleRoomClick(room.id)}
          />
        ))}

        {/* Creatures */}
        <div ref={mapRef} className="absolute inset-0 pointer-events-none" style={{ zIndex: 5 }}>
          {CREATURES.map((creature) => (
            <Creature key={creature.id} creature={creature} mapRef={mapRef} />
          ))}
        </div>

        {/* Creature legend */}
        <CreatureLegend />

        {/* Side panel */}
        <AnimatePresence>
          {activeRoom && (
            <SidePanel
              key={activeRoom}
              roomId={activeRoom}
              onClose={() => setActiveRoom(null)}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
