import React from "react";
import { Composition } from "remotion";
import { DemoReel } from "./compositions/DemoReel";
import { PitchDeck } from "./compositions/PitchDeck";
import { SLIDES } from "./data/copy";
import {
  fps,
  height,
  reelDurationInFrames,
  slideDurationInFrames,
  width,
} from "./theme";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PitchDeck"
        component={PitchDeck}
        durationInFrames={SLIDES.length * slideDurationInFrames}
        fps={fps}
        width={width}
        height={height}
      />
      <Composition
        id="DemoReel"
        component={DemoReel}
        durationInFrames={reelDurationInFrames}
        fps={fps}
        width={width}
        height={height}
      />
    </>
  );
};
