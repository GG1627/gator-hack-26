import { loadFont } from "@remotion/fonts";
import {
  AbsoluteFill,
  Sequence,
  Track,
  staticFile,
  useCurrentFrame,
} from "remotion";
import plan from "../../film-plan.json";
import voice from "./voice-preview.json";
import audio from "./audio-config.json";
import {
  Hook,
  Premise,
  Demo,
  Result,
  Causality,
  Gaussians,
  Frontier,
  Benchmark,
  Difficulty,
  Limits,
  Close,
} from "./scenes";
import { DraftTag } from "./primitives";
import { SceneMotion } from "./SceneMotion";
import { Soundtrack } from "../Soundtrack";
import { color } from "./theme";
loadFont({
  family: "Manrope",
  url: staticFile("fonts/manrope.woff2"),
  weight: "200 800",
});
export type FilmProps = {
  draftScript: boolean;
  draftOverlays: boolean;
  narration: boolean;
  captions: boolean;
  musicEnabled: boolean;
};
const ScriptPreview = () => {
  const f = useCurrentFrame();
  const scene = plan.scenes.find(
    (s) => f >= s.from && f < s.from + s.durationInFrames,
  );
  if (!scene) return null;
  return (
    <div
      style={{
        position: "absolute",
        bottom: 20,
        left: 180,
        right: 180,
        fontSize: 25,
        color: color.paper,
        background: color.ink,
        padding: 16,
      }}
    >
      Script reference: {scene.narration}
    </div>
  );
};
export const SubmissionFilm = ({
  draftScript,
  draftOverlays,
  narration,
  captions,
  musicEnabled,
}: FilmProps) => (
  <AbsoluteFill
    style={{ fontFamily: "Manrope, sans-serif", background: color.ink }}
  >
    <Track name="Film scenes">
      <Sequence
        name="01 · When to look"
        durationInFrames={plan.scenes[0].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[0].durationInFrames}>
          <Hook />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="02 · Meet Peekaboo"
        from={plan.scenes[1].from}
        durationInFrames={plan.scenes[1].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[1].durationInFrames}>
          <Premise />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="03 · Recorded comparison"
        from={plan.scenes[2].from}
        durationInFrames={plan.scenes[2].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[2].durationInFrames} recorded>
          <Demo />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="04 · Measured result"
        from={plan.scenes[3].from}
        durationInFrames={plan.scenes[3].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[3].durationInFrames}>
          <Result />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="05 · Causal decision boundary"
        from={plan.scenes[4].from}
        durationInFrames={plan.scenes[4].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[4].durationInFrames}>
          <Causality />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="06 · Gaussian representation"
        from={plan.scenes[5].from}
        durationInFrames={plan.scenes[5].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[5].durationInFrames}>
          <Gaussians />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="07 · Recent native CUDA Rust"
        from={plan.scenes[6].from}
        durationInFrames={plan.scenes[6].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[6].durationInFrames}>
          <Frontier />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="08 · Rendering benchmark"
        from={plan.scenes[7].from}
        durationInFrames={plan.scenes[7].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[7].durationInFrames}>
          <Benchmark />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="09 · Engineering challenges"
        from={plan.scenes[8].from}
        durationInFrames={plan.scenes[8].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[8].durationInFrames}>
          <Difficulty />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="10 · Evidence and limits"
        from={plan.scenes[9].from}
        durationInFrames={plan.scenes[9].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[9].durationInFrames}>
          <Limits />
        </SceneMotion>
      </Sequence>
      <Sequence
        name="11 · See more. Illuminate less."
        from={plan.scenes[10].from}
        durationInFrames={plan.scenes[10].durationInFrames}
      >
        <SceneMotion duration={plan.scenes[10].durationInFrames}>
          <Close />
        </SceneMotion>
      </Sequence>
    </Track>
    <Soundtrack
      voiceClips={narration ? voice.clips : []}
      cues={audio.effects}
      musicTrack={musicEnabled ? audio.music : null}
      captionsEnabled={captions}
    />
    {draftScript ? <ScriptPreview /> : null}
    {draftOverlays ? <DraftTag /> : null}
  </AbsoluteFill>
);
