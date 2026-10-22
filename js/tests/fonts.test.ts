import { expect, setDefaultTimeout, test } from "bun:test";

import { loadRenderCV } from "../src/index.ts";

// RenderCV's fonts are a 33 MB download:
setDefaultTimeout(600_000);

test("installs RenderCV's fonts by default", async () => {
  const rendercv = await loadRenderCV();

  const cv = await rendercv.render({ yaml: "cv:\n  name: Jane Doe\n  email: jane@example.com\n" });

  const pdf = new TextDecoder("latin1").decode(cv.pdf);
  // The classic design's font, and the icons' font:
  expect(pdf).toContain("SourceSans3");
  expect(pdf).toContain("FontAwesome");
});
