// PCM WAV edits happen at sample boundaries, with no resampling/time stretching.
// Preserve unknown metadata chunks by writing a standard PCM container instead.
export function pcmWav(bytes) {
  if (
    bytes.toString("ascii", 0, 4) !== "RIFF" ||
    bytes.toString("ascii", 8, 12) !== "WAVE"
  )
    throw Error("Expected RIFF WAV.");
  let format, data;
  for (let p = 12; p + 8 <= bytes.length; ) {
    const kind = bytes.toString("ascii", p, p + 4);
    const n = bytes.readUInt32LE(p + 4);
    if (p + 8 + n > bytes.length) throw Error("Truncated WAV.");
    if (kind === "fmt ") format = bytes.subarray(p + 8, p + 8 + n);
    if (kind === "data") data = bytes.subarray(p + 8, p + 8 + n);
    p += 8 + n + (n % 2);
  }
  if (!format || !data) throw Error("Missing PCM WAV chunks.");
  const code = format.readUInt16LE(0),
    channels = format.readUInt16LE(2),
    sampleRate = format.readUInt32LE(4),
    blockAlign = format.readUInt16LE(12),
    bits = format.readUInt16LE(14);
  if (![1, 65534].includes(code) || ![16, 24, 32].includes(bits))
    throw Error("Expected signed PCM waveform.");
  return { format, data, channels, sampleRate, blockAlign, bits };
}
export function paddedWav(
  bytes,
  { leadSeconds = 0.18, tailSeconds = 0.15, startSeconds = 0, endSeconds } = {},
) {
  const wave = pcmWav(bytes);
  const frameCount = wave.data.length / wave.blockAlign;
  const first = Math.max(0, Math.floor(startSeconds * wave.sampleRate));
  const last = Math.min(
    frameCount,
    endSeconds === undefined
      ? frameCount
      : Math.ceil(endSeconds * wave.sampleRate),
  );
  if (last <= first) throw Error("Invalid source range.");
  const leadFrames = Math.round(leadSeconds * wave.sampleRate),
    tailFrames = Math.round(tailSeconds * wave.sampleRate);
  const payload = Buffer.concat([
    Buffer.alloc(leadFrames * wave.blockAlign),
    wave.data.subarray(first * wave.blockAlign, last * wave.blockAlign),
    Buffer.alloc(tailFrames * wave.blockAlign),
  ]);
  const formatChunk = Buffer.alloc(
    8 + wave.format.length + (wave.format.length % 2),
  );
  formatChunk.write("fmt ", 0);
  formatChunk.writeUInt32LE(wave.format.length, 4);
  wave.format.copy(formatChunk, 8);
  const dataHeader = Buffer.alloc(8);
  dataHeader.write("data", 0);
  dataHeader.writeUInt32LE(payload.length, 4);
  const header = Buffer.alloc(12);
  header.write("RIFF", 0);
  header.writeUInt32LE(
    4 + formatChunk.length + 8 + payload.length + (payload.length % 2),
    4,
  );
  header.write("WAVE", 8);
  return {
    buffer: Buffer.concat([
      header,
      formatChunk,
      dataHeader,
      payload,
      ...(payload.length % 2 ? [Buffer.alloc(1)] : []),
    ]),
    seconds: payload.length / wave.blockAlign / wave.sampleRate,
    sourceFirstSeconds: first / wave.sampleRate,
    leadSeconds: leadFrames / wave.sampleRate,
  };
}
