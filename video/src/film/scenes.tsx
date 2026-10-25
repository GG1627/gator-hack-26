import {
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Canvas, Enter, Eyebrow, Note, Rule, Title } from "./primitives";
import {
  AcquisitionBoundary,
  GaussianSurface,
  NativeRenderFlow,
  OpticalSignal,
} from "./diagrams";
import { Footage } from "./footage";
import { color, ease } from "./theme";
import evidence from "./evidence.json";
import plan from "../../film-plan.json";
import { SceneMotion } from "./SceneMotion";

export const Hook = () => (
  <Canvas>
    <OpticalSignal />
    <div style={{ position: "relative", marginTop: 230 }}>
      <Enter>
        <Title style={{ fontSize: 104, maxWidth: 1280 }}>
          What if a microscope
          <br />
          knew exactly when
          <br />
          to take its next picture?
        </Title>
      </Enter>
    </div>
  </Canvas>
);

const ObservationCost = () => {
  const f = useCurrentFrame();
  return (
    <Canvas>
      <Eyebrow>The cost of looking · published research</Eyebrow>
      <Enter>
        <Title style={{ fontSize: 64, maxWidth: 1500 }}>
          Imaging light can change the biology.
        </Title>
      </Enter>
      <div
        style={{
          position: "absolute",
          right: 180,
          top: 315,
          width: 330,
          height: 330,
          borderRadius: "50%",
          border: `1px solid ${color.amber}`,
          background: `radial-gradient(circle, #e9b669${Math.round(
            interpolate(f, [0, 45, 90], [20, 90, 35], ease),
          )
            .toString(16)
            .padStart(2, "0")}, transparent 70%)`,
        }}
      />
      <Enter at={18}>
        <div
          style={{
            fontSize: 258,
            lineHeight: 1,
            letterSpacing: -14,
            fontWeight: 750,
            color: color.butter,
            marginTop: 52,
          }}
        >
          80<span style={{ fontSize: 130 }}>%</span>
        </div>
        <div style={{ fontSize: 51, fontWeight: 600, marginTop: 22 }}>
          fewer mitotic events
        </div>
        <div style={{ fontSize: 31, color: color.muted, marginTop: 28 }}>
          CHO cells · high-dose near-UV exposure · 60 J/cm²
        </div>
      </Enter>
      <Note>
        PhotoFiTT · Nature Communications (2025) · Supplementary Fig. S1a
        <br />
        doi:10.1038/s41467-025-66209-6
      </Note>
    </Canvas>
  );
};
const Brand = ({ closing = false }: { closing?: boolean }) => {
  const f = useCurrentFrame();
  return (
    <Canvas light>
      <Eyebrow>
        {closing ? "A better moment to look." : "Meet Peekaboo."}
      </Eyebrow>
      <Enter style={{ marginTop: 180 }}>
        <Title style={{ fontSize: 160, letterSpacing: -9 }}>Peekaboo.</Title>
        <p
          style={{
            fontSize: 45,
            fontWeight: 600,
            letterSpacing: -1,
            marginTop: 38,
          }}
        >
          See more. Illuminate less.
        </p>
        <p
          style={{
            fontSize: 31,
            lineHeight: 1.6,
            maxWidth: 820,
            marginTop: 30,
          }}
        >
          {closing ? (
            "Capture the moments that matter."
          ) : (
            <>
              Software that chooses when
              <br />
              to take the next microscopy image.
            </>
          )}
        </p>
      </Enter>
      <Img
        src={staticFile("brand/capybara.png")}
        style={{
          position: "absolute",
          width: 690,
          height: 710,
          objectFit: "contain",
          right: 65,
          top: 170,
          opacity: interpolate(f, [4, 30], [0, 1], ease),
          translate: `${interpolate(f, [0, 45], [80, 0], ease)}px ${interpolate(f, [0, 45], [24, 0], ease)}px`,
          scale: interpolate(f, [0, 32, 56], [0.91, 1.015, 1], ease),
        }}
      />
      {closing ? (
        <Note>GatorHack V · 2026 · github.com/GG1627/gator-hack-26</Note>
      ) : null}
    </Canvas>
  );
};
const NarrativeBeat = ({
  title,
  eyebrow,
}: {
  title: string;
  eyebrow: string;
}) => (
  <Canvas>
    <OpticalSignal />
    <Eyebrow>{eyebrow}</Eyebrow>
    <Enter style={{ position: "relative", marginTop: 230 }}>
      <Title style={{ fontSize: 88, maxWidth: 1040 }}>{title}</Title>
    </Enter>
  </Canvas>
);

export const Premise = () => (
  <>
    <Sequence
      name="Every image costs light"
      durationInFrames={plan.visualTimings.premiseResearch}
    >
      <SceneMotion duration={plan.visualTimings.premiseResearch}>
        <NarrativeBeat
          eyebrow="The cost of looking"
          title="Imaging light can change a living cell."
        />
      </SceneMotion>
    </Sequence>
    <Sequence
      name="Published phototoxicity result"
      from={plan.visualTimings.premiseResearch}
      durationInFrames={
        plan.visualTimings.premiseQuestion - plan.visualTimings.premiseResearch
      }
    >
      <SceneMotion
        duration={
          plan.visualTimings.premiseQuestion -
          plan.visualTimings.premiseResearch
        }
      >
        <ObservationCost />
      </SceneMotion>
    </Sequence>
    <Sequence
      name="A better time to look"
      from={plan.visualTimings.premiseQuestion}
      durationInFrames={
        plan.visualTimings.premiseBrand - plan.visualTimings.premiseQuestion
      }
    >
      <SceneMotion
        duration={
          plan.visualTimings.premiseBrand - plan.visualTimings.premiseQuestion
        }
      >
        <NarrativeBeat
          eyebrow="A smarter capture schedule"
          title="What if the microscope knew when to wait?"
        />
      </SceneMotion>
    </Sequence>
    <Sequence
      name="Meet Peekaboo"
      from={plan.visualTimings.premiseBrand}
      durationInFrames={
        plan.scenes[1].durationInFrames - plan.visualTimings.premiseBrand
      }
    >
      <SceneMotion
        duration={
          plan.scenes[1].durationInFrames - plan.visualTimings.premiseBrand
        }
      >
        <Brand />
      </SceneMotion>
    </Sequence>
  </>
);

export const Demo = () => (
  <>
    {plan.visualTimings.demoPlayback > 0 ? (
      <Sequence
        name="Comparison setup"
        durationInFrames={plan.visualTimings.demoPlayback}
      >
        <SceneMotion duration={plan.visualTimings.demoPlayback}>
          <Canvas>
            <Eyebrow>One controlled experiment</Eyebrow>
            <Title style={{ marginTop: 150 }}>
              Two ways to choose
              <br />
              the next picture.
            </Title>
            <div
              style={{ display: "flex", gap: 150, marginTop: 75, fontSize: 45 }}
            >
              <span style={{ color: color.blue }}>Fixed intervals</span>
              <span style={{ color: color.amber }}>Peekaboo</span>
            </div>
          </Canvas>
        </SceneMotion>
      </Sequence>
    ) : null}
    <Sequence
      name="Complete recorded comparison"
      from={plan.visualTimings.demoPlayback}
      durationInFrames={660}
    >
      <Footage src="recordings/demo-304.mp4" trim={90} duration={660} />
    </Sequence>
  </>
);

const ResultCard = () => {
  const f = useCurrentFrame();
  return (
    <Canvas>
      <Eyebrow>The selected example</Eyebrow>
      <Title>
        Better timing.
        <br />
        Fewer exposures.
      </Title>
      <div style={{ display: "flex", gap: 120, marginTop: 60 }}>
        <Enter at={0}>
          <div style={{ fontSize: 27, color: color.blue, marginBottom: 14 }}>
            Fixed schedule
          </div>
          <div style={{ fontSize: 116, fontWeight: 700, letterSpacing: -6 }}>
            {evidence.featured.fixedImages}
            <span
              style={{ fontSize: 35, letterSpacing: -1, color: color.muted }}
            >
              {" "}
              images
            </span>
          </div>
          <div style={{ fontSize: 39, color: color.blue }}>
            {evidence.featured.fixedCovered}/{evidence.featured.events}{" "}
            divisions covered
          </div>
        </Enter>
        <Enter at={15}>
          <div style={{ fontSize: 27, color: color.amber, marginBottom: 14 }}>
            Peekaboo
          </div>
          <div style={{ fontSize: 116, fontWeight: 700, letterSpacing: -6 }}>
            {evidence.featured.adaptiveImages}
            <span
              style={{ fontSize: 35, letterSpacing: -1, color: color.muted }}
            >
              {" "}
              images
            </span>
          </div>
          <div style={{ fontSize: 39, color: color.amber }}>
            {evidence.featured.adaptiveCovered}/{evidence.featured.events}{" "}
            divisions covered
          </div>
        </Enter>
        <Enter
          at={80}
          style={{
            marginLeft: 30,
            paddingLeft: 60,
            borderLeft: `1px solid ${color.line}`,
          }}
        >
          <div
            style={{
              fontSize: 116,
              fontWeight: 700,
              color: color.butter,
              letterSpacing: -6,
            }}
          >
            {Math.round(evidence.featured.exposureReduction * 100)}
            <span style={{ fontSize: 60 }}>%</span>
          </div>
          <div style={{ fontSize: 34, maxWidth: 290, lineHeight: 1.3 }}>
            fewer exposures
          </div>
        </Enter>
      </div>
      <div
        style={{
          position: "absolute",
          right: 110,
          top: 120,
          opacity: interpolate(f, [90, 115], [0, 1], ease),
          fontSize: 24,
          color: color.muted,
        }}
      >
        Same 240-frame experiment
      </div>
      <Note>
        Selected after evaluation · seed 304 · coverage within ±1 source frame
        <br />
        Equal illumination per image assumed for light reduction · no
        cell-health outcome measured
      </Note>
    </Canvas>
  );
};
export const Result = () => (
  <>
    <Sequence name="Actual result reveal" durationInFrames={105}>
      <Footage
        src="recordings/featured-result.mp4"
        trim={90}
        duration={105}
        label="Recorded app · selected example results"
      />
    </Sequence>
    <Sequence
      name="Measured comparison"
      from={105}
      durationInFrames={plan.scenes[3].durationInFrames - 105}
    >
      <SceneMotion duration={plan.scenes[3].durationInFrames - 105}>
        <ResultCard />
      </SceneMotion>
    </Sequence>
  </>
);

export const Causality = () => (
  <Canvas>
    <Eyebrow>Observe → estimate → decide</Eyebrow>
    <Enter>
      <Title>No peeking ahead.</Title>
      <p style={{ fontSize: 37, color: color.muted, marginTop: 28 }}>
        Only acquired images guide the next capture.
      </p>
    </Enter>
    <div style={{ marginTop: 70 }}>
      <AcquisitionBoundary />
    </div>
    <Note>Controller runs within image-budget and gap constraints</Note>
  </Canvas>
);

const GaussianConcept = () => (
  <Canvas>
    <Eyebrow>A compact cell model</Eyebrow>
    <Title>Position. Brightness. Shape.</Title>
    <div
      style={{ display: "flex", alignItems: "center", gap: 45, marginTop: 25 }}
    >
      <GaussianSurface />
      <div style={{ flex: 1 }}>
        <Enter>
          <div style={{ fontSize: 31, color: color.muted, marginBottom: 26 }}>
            Acquired-image shape cue
          </div>
          <div style={{ fontSize: 56, fontWeight: 650, lineHeight: 1.2 }}>
            Visible elongation.
            <br />
            Shorter capture gaps.
          </div>
        </Enter>
        <Enter at={100}>
          <Rule />
          <div style={{ fontSize: 32, color: color.amber }}>
            12 → 4 → 2 frames
          </div>
          <p style={{ fontSize: 26, color: color.muted, lineHeight: 1.5 }}>
            Heuristic target gaps, subject to
            <br />
            budget and coverage guards.
          </p>
        </Enter>
      </div>
    </div>
    <Note>
      Inspired by CellSplat4D · arXiv:2610.04199 · 3 Oct 2026
      <br />
      Simplified observation model; not a reproduction of the complete paper
    </Note>
  </Canvas>
);
export const Gaussians = () => (
  <>
    <Sequence name="Actual Gaussian controls" durationInFrames={150}>
      <Footage
        src="recordings/gaussian-controls.mp4"
        trim={90}
        duration={150}
        label="Recorded app · model controls and saved acquired-image fit"
      />
    </Sequence>
    <Sequence
      name="Shape explains timing"
      from={150}
      durationInFrames={plan.scenes[5].durationInFrames - 150}
    >
      <SceneMotion duration={plan.scenes[5].durationInFrames - 150}>
        <GaussianConcept />
      </SceneMotion>
    </Sequence>
  </>
);

const FrontierTitle = () => (
  <Canvas>
    <Eyebrow>Fresh off the frontier</Eyebrow>
    <Enter>
      <Title style={{ fontSize: 120 }}>
        Native GPU kernels.
        <br />
        Written in Rust.
      </Title>
    </Enter>
    <Enter at={35}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: 60,
          marginTop: 70,
        }}
      >
        <span style={{ fontSize: 55, color: color.amber }}>
          NVIDIA cuTile Rust
        </span>
        <span style={{ fontSize: 32, color: color.muted }}>
          Initial tagged release · 7 Apr 2026
        </span>
      </div>
    </Enter>
    <Note>
      Source: NVlabs/cutile-rs CHANGELOG · NVIDIA CUDA Rust announcement: 8 Sep
      2026
    </Note>
  </Canvas>
);
const FrontierFlow = () => (
  <Canvas>
    <Eyebrow>Our scientific rendering path</Eyebrow>
    <Title>
      From cell parameters
      <br />
      to model images.
    </Title>
    <NativeRenderFlow />
    <Note>
      CPU fits shapes and chooses captures · GPU renders models
      <br />
      Browser replays previously exported results
    </Note>
  </Canvas>
);
export const Frontier = () => (
  <>
    <Sequence name="Recent tooling" durationInFrames={90}>
      <FrontierTitle />
    </Sequence>
    <Sequence
      name="Native scientific rendering"
      from={90}
      durationInFrames={210}
    >
      <SceneMotion duration={210}>
        <FrontierFlow />
      </SceneMotion>
    </Sequence>
    <Sequence
      name="Actual cuTile model view"
      from={300}
      durationInFrames={plan.scenes[6].durationInFrames - 300}
    >
      <Footage
        src="recordings/cuda-tiles.mp4"
        trim={90}
        duration={plan.scenes[6].durationInFrames - 300}
        label="Recorded app · native render workflow and saved output"
      />
    </Sequence>
  </>
);

export const Benchmark = () => {
  const f = useCurrentFrame();
  return (
    <Canvas>
      <Eyebrow>Measured dense rendering</Eyebrow>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "end",
        }}
      >
        <Title>{evidence.benchmark.ratio.toFixed(1)}× faster.</Title>
        <div style={{ fontSize: 29, color: color.muted, paddingBottom: 12 }}>
          10,000 Gaussians · 64 × 64 output
        </div>
      </div>
      <div style={{ marginTop: 85 }}>
        {[
          {
            name: "CPU reference",
            ms: evidence.benchmark.cpuMs,
            ink: color.blue,
          },
          {
            name: "GPU · persistent worker",
            ms: evidence.benchmark.gpuMs,
            ink: color.amber,
          },
        ].map((b, i) => (
          <div key={b.name} style={{ marginBottom: 45 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: 31,
                marginBottom: 18,
              }}
            >
              <span>{b.name}</span>
              <span>{Math.round(b.ms).toLocaleString("en-US")} ms</span>
            </div>
            <div
              style={{ height: 72, background: "#ffffff08", borderRadius: 5 }}
            >
              <div
                style={{
                  height: 72,
                  borderRadius: 5,
                  background: b.ink,
                  width:
                    interpolate(
                      f,
                      [45 + i * 10, 100 + i * 10],
                      [0, (b.ms / evidence.benchmark.cpuMs) * 100],
                      ease,
                    ) + "%",
                }}
              />
            </div>
          </div>
        ))}
      </div>
      <Note>
        Warmed full rendering call · startup excluded · medians of 15 calls
        <br />
        Renderer benchmark, not whole-application speedup ·
        docs/cuda-latency-audit.md
      </Note>
    </Canvas>
  );
};

export const Difficulty = () => {
  const f = useCurrentFrame();
  return (
    <Canvas>
      <Eyebrow>What took engineering</Eyebrow>
      <Title>
        Make it correct.
        <br />
        Then make reuse count.
      </Title>
      <div style={{ display: "flex", gap: 110, marginTop: 65 }}>
        <Enter style={{ flex: 1 }}>
          <div style={{ fontSize: 29, color: color.blue }}>
            01 / Numerical agreement
          </div>
          <p style={{ fontSize: 42, lineHeight: 1.3 }}>
            GPU output checked
            <br />
            against a CPU reference.
          </p>
          <div style={{ fontSize: 26, color: color.muted }}>
            Sampled export error &lt; 2 × 10⁻⁶ tolerance
          </div>
        </Enter>
        <div
          style={{ flex: 1, opacity: interpolate(f, [130, 160], [0, 1], ease) }}
        >
          <div style={{ fontSize: 29, color: color.amber }}>
            02 / Persistent worker
          </div>
          <p style={{ fontSize: 42, lineHeight: 1.3 }}>
            Start once.
            <br />
            Render repeatedly.
          </p>
          <div style={{ fontSize: 26, color: color.muted }}>
            CPU path retained where GPU overhead dominates.
          </div>
        </div>
      </div>
      <Note>
        Implementation evidence: CPU parity checks, persistent-worker latency
        audit and fallback tests
      </Note>
    </Canvas>
  );
};

const RealDataBoundary = () => (
  <Canvas>
    <Eyebrow>What the evidence supports</Eyebrow>
    <Enter>
      <Title>
        Real microscopy is
        <br />
        the next hard test.
      </Title>
    </Enter>
    <Enter at={25}>
      <p
        style={{
          fontSize: 42,
          lineHeight: 1.45,
          maxWidth: 1430,
          marginTop: 55,
        }}
      >
        Our separate real-microscopy benchmark did not
        <br />
        improve division coverage over fixed timing.
      </p>
    </Enter>
    <Enter at={65}>
      <p
        style={{
          fontSize: 30,
          lineHeight: 1.5,
          color: color.muted,
          maxWidth: 1400,
        }}
      >
        It used an earlier frozen controller. Controlled timing results motivate
        <br />
        further validation; cell-health benefit has not been measured.
      </p>
    </Enter>
    <Note>
      Completed Phase 5 evaluation · MSKCC-CONFOCAL · held-out C. elegans
      sequences
      <br />
      Evidence and limitations: docs/DEMO_PREP.md
    </Note>
  </Canvas>
);
export const Limits = () => (
  <>
    <Sequence
      name="Actual adverse outcome"
      durationInFrames={plan.visualTimings.limitsFootage}
    >
      <Footage
        src="recordings/abrupt-304.mp4"
        trim={150}
        duration={plan.visualTimings.limitsFootage}
        label="Recorded app · sudden divisions · selected adverse example"
      />
    </Sequence>
    <Sequence
      name="Real-data evidence boundary"
      from={plan.visualTimings.limitsFootage}
      durationInFrames={
        plan.scenes[9].durationInFrames - plan.visualTimings.limitsFootage
      }
    >
      <SceneMotion
        duration={
          plan.scenes[9].durationInFrames - plan.visualTimings.limitsFootage
        }
      >
        <RealDataBoundary />
      </SceneMotion>
    </Sequence>
  </>
);
export const Close = () => (
  <>
    <Sequence
      name="The moments that matter"
      durationInFrames={plan.visualTimings.closeBrand}
    >
      <SceneMotion duration={plan.visualTimings.closeBrand}>
        <NarrativeBeat
          eyebrow="Our next step: validate on real microscopes"
          title="Capture the moments that matter. Use less light."
        />
      </SceneMotion>
    </Sequence>
    <Sequence
      name="See more. Illuminate less."
      from={plan.visualTimings.closeBrand}
      durationInFrames={
        plan.scenes[10].durationInFrames - plan.visualTimings.closeBrand
      }
    >
      <SceneMotion
        duration={
          plan.scenes[10].durationInFrames - plan.visualTimings.closeBrand
        }
      >
        <Brand closing />
      </SceneMotion>
    </Sequence>
  </>
);
