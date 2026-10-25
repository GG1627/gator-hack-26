import { Composition } from "remotion";
import { ProofOfStyle } from "./Composition";
import { SubmissionFilm } from "./film/Film";
import plan from "../film-plan.json";

export const RemotionRoot = () => (
  <>
    <Composition
      id="Peekaboo-StyleStudy"
      component={ProofOfStyle}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={300}
      defaultProps={{ tagline: "See more. Illuminate less." }}
    />
    <Composition
      id="Peekaboo-Submission"
      component={SubmissionFilm}
      width={1920}
      height={1080}
      fps={30}
      durationInFrames={plan.durationInFrames}
      defaultProps={{
        draftScript: false,
        draftOverlays: false,
        narration: true,
        captions: true,
        musicEnabled: true,
      }}
    />
  </>
);
