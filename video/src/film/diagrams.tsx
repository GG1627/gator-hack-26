import { interpolate, useCurrentFrame } from "remotion";
import { color, ease } from "./theme";

export const OpticalSignal = () => {
  const f = useCurrentFrame();
  return (
    <svg
      viewBox="0 0 1920 1080"
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
    >
      <defs>
        <radialGradient id="film-signal">
          <stop stopColor={color.amber} stopOpacity=".55" />
          <stop offset="1" stopColor={color.amber} stopOpacity="0" />
        </radialGradient>
      </defs>
      <g
        opacity={interpolate(f, [0, 32], [0, 1], ease)}
        style={{
          transformOrigin: "1490px 520px",
          rotate: `${interpolate(f, [0, 141], [-5, 2], ease)}deg`,
          scale: interpolate(f, [0, 141], [0.88, 1.04], ease),
        }}
      >
        <ellipse
          cx="1490"
          cy="520"
          rx="360"
          ry="280"
          fill="url(#film-signal)"
        />
        {[1, 0.72, 0.4].map((s) => (
          <ellipse
            key={s}
            cx="1490"
            cy="520"
            rx={280 * s}
            ry={190 * s}
            fill="none"
            stroke={color.amber}
            strokeOpacity=".45"
            strokeWidth="1.5"
            transform="rotate(-25 1490 520)"
          />
        ))}
        <path
          d="M1150 520H1820M1490 200V840"
          stroke={color.amber}
          strokeOpacity=".2"
          strokeDasharray="4 12"
        />
        <circle cx="1490" cy="520" r="5" fill={color.butter} />
      </g>
    </svg>
  );
};

export const AcquisitionBoundary = () => {
  const f = useCurrentFrame();
  return (
    <svg viewBox="0 0 1700 510" width="1700" height="510">
      <line
        x1="60"
        y1="280"
        x2="1640"
        y2="280"
        stroke={color.line}
        strokeWidth="2"
      />
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <g key={i} opacity={i > 3 ? 0.27 : 1}>
          <rect
            x={65 + i * 210}
            y="160"
            width="125"
            height="125"
            rx="12"
            fill={i <= 3 ? "#3f4648" : "none"}
            stroke={i <= 3 ? color.amber : color.muted}
            strokeWidth="2"
          />
          {i <= 3 ? (
            <ellipse
              cx={128 + i * 210}
              cy="222"
              rx={20 + i * 5}
              ry="18"
              fill={color.amber}
              opacity=".8"
            />
          ) : (
            <text
              x={128 + i * 210}
              y="238"
              textAnchor="middle"
              fill={color.muted}
              fontSize="38"
            >
              ?
            </text>
          )}
          <text
            x={128 + i * 210}
            y="330"
            textAnchor="middle"
            fill={color.paper}
            fontSize="24"
          >
            {i <= 3 ? "Acquired" : "Hidden"}
          </text>
        </g>
      ))}
      <line
        x1="850"
        y1="90"
        x2="850"
        y2="380"
        stroke={color.blue}
        strokeWidth="2"
        strokeDasharray="6 8"
      />
      <text x="850" y="60" textAnchor="middle" fill={color.blue} fontSize="30">
        Decision time
      </text>
      <g opacity={interpolate(f, [90, 120], [0, 1], ease)}>
        <path d="M420 395H780" stroke={color.amber} strokeWidth="2" />
        <text x="60" y="440" fill={color.butter} fontSize="34">
          Measure shape
        </text>
        <text x="550" y="440" fill={color.butter} fontSize="34">
          Choose next capture
        </text>
      </g>
      <text x="1070" y="440" fill={color.muted} fontSize="30">
        Reserved for later evaluation
      </text>
    </svg>
  );
};

export const GaussianSurface = () => {
  const f = useCurrentFrame();
  const stretch = interpolate(f, [80, 200], [1, 1.75], ease);
  return (
    <svg viewBox="0 0 900 560" width="900" height="560">
      <defs>
        <radialGradient id="gaussian">
          <stop stopColor="#ffe2a0" />
          <stop offset=".45" stopColor={color.amber} stopOpacity=".5" />
          <stop offset="1" stopColor={color.amber} stopOpacity="0" />
        </radialGradient>
      </defs>
      <path
        d="M100 400H820M450 100V490"
        stroke={color.line}
        strokeDasharray="5 10"
      />
      <ellipse
        cx="450"
        cy="300"
        rx={160 * stretch}
        ry="160"
        fill="url(#gaussian)"
      />
      {[1, 0.75, 0.5, 0.25].map((s) => (
        <ellipse
          key={s}
          cx="450"
          cy="300"
          rx={145 * s * stretch}
          ry={145 * s}
          fill="none"
          stroke={color.amber}
          strokeOpacity=".6"
        />
      ))}
      <circle cx="450" cy="300" r="5" fill={color.paper} />
      <text
        x="450"
        y="520"
        textAnchor="middle"
        fill={color.muted}
        fontSize="25"
      >
        Gaussian intensity field
      </text>
    </svg>
  );
};

export const NativeRenderFlow = () => {
  const f = useCurrentFrame();
  return (
    <div
      style={{ display: "flex", gap: 30, alignItems: "center", marginTop: 60 }}
    >
      {[
        {
          title: "Gaussian parameters",
          detail: "CPU · acquired-image fit",
          label: "Position / brightness / shape",
        },
        {
          title: "Native Rust kernel",
          detail: "GPU · cuTile",
          label: "Tile-based intensity accumulation",
        },
        {
          title: "Model image",
          detail: "Saved scientific output",
          label: "CPU-reference checks",
        },
      ].map((x, i) => (
        <div
          key={x.title}
          style={{
            flex: 1,
            opacity: interpolate(f, [i * 25, i * 25 + 24], [0, 1], ease),
          }}
        >
          <div
            style={{
              borderTop: `2px solid ${i === 1 ? color.amber : color.blue}`,
              paddingTop: 30,
            }}
          >
            <div
              style={{
                fontSize: 24,
                color: i === 1 ? color.amber : color.blue,
                marginBottom: 28,
              }}
            >
              {x.detail}
            </div>
            <div
              style={{
                fontSize: 43,
                fontWeight: 650,
                lineHeight: 1.2,
                minHeight: 110,
              }}
            >
              {x.title}
            </div>
            <div style={{ fontSize: 26, color: color.muted, lineHeight: 1.4 }}>
              {x.label}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
