//! Native Rust cuTile Gaussian accumulation. No microscopy files or event labels.
use cuda_core::IntoResult;
use cutile::prelude::*;
use serde::Deserialize;
use serde_json::json;
use std::fs;
use std::io::{BufRead, Read, Write};
use std::sync::Arc;
use std::time::Instant;

#[cutile::module]
mod photon_kernel {
    use cutile::core::*;

    #[cutile::entry()]
    fn render(
        output: &mut Tensor<f32, { [1, 1, 128] }>,
        boundary: &mut Tensor<i32, { [1, 1, 128] }>,
        gaussians: &Tensor<f64, { [-1, -1, 16] }>,
        counts: &Tensor<i32, { [-1] }>,
        height: i32,
        width: i32,
        pixels: i32,
        truncate_squared: f64,
    ) {
        let pid = get_tile_block_id();
        let block_start = (pid.1 * 64 + pid.2) * 128;
        let offset =
            iota::<i32, { [128] }>(shape![128]) + broadcast_scalar(block_start, shape![128]);
        let iz = offset / broadcast_scalar(height * width, shape![128]);
        let iy =
            (offset / broadcast_scalar(width, shape![128])) % broadcast_scalar(height, shape![128]);
        let ix = offset % broadcast_scalar(width, shape![128]);
        let z: Tile<f64, { [1, 1, 128] }> = convert_tile(iz.reshape(shape![1, 1, 128]));
        let y: Tile<f64, { [1, 1, 128] }> = convert_tile(iy.reshape(shape![1, 1, 128]));
        let x: Tile<f64, { [1, 1, 128] }> = convert_tile(ix.reshape(shape![1, 1, 128]));
        let mut n =
            tile_to_scalar::<i32, i32>(counts.load_tile(shape![1], [pid.0]).reshape(shape![]));
        if block_start >= pixels {
            n = 0;
        }
        let zero = broadcast_scalar(0.0f32, shape![1, 1, 128]);
        let cutoff = broadcast_scalar(truncate_squared, shape![1, 1, 128]);
        let one64 = broadcast_scalar(1.0f64, shape![1, 1, 128]);
        let epsilon = broadcast_scalar(1e-12f64, shape![1, 1, 128]);
        let minus_half = broadcast_scalar(-0.5f64, shape![1, 1, 128]);
        let mut sum = zero;
        let mut edge = broadcast_scalar(0i32, shape![1, 1, 128]);
        for g in 0i32..n {
            let cz = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 0])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let cy = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 1])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let cx = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 2])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let dz = z - cz;
            let dy = y - cy;
            let dx = x - cx;
            let p00 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 3])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let p01 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 4])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let p02 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 5])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let p10 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 6])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let p11 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 7])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let p12 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 8])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let p20 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 9])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let p21 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 10])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let p22 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 11])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let amplitude64 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 12])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let precision_l1 = gaussians
                .load_tile(shape![1, 1, 1], [pid.0, g, 13])
                .reshape(shape![1, 1, 1])
                .broadcast(shape![1, 1, 128]);
            let mut q = dz * p00 * dz;
            q = q + dz * p01 * dy;
            q = q + dz * p02 * dx;
            q = q + dy * p10 * dz;
            q = q + dy * p11 * dy;
            q = q + dy * p12 * dx;
            q = q + dx * p20 * dz;
            q = q + dx * p21 * dy;
            q = q + dx * p22 * dx;
            // FP64 geometry protects thin anisotropic components. Flag the hard
            // cutoff band for CPU FP64 repair; exponent/value accumulation is FP32.
            let radius_l1 = absf(dz) + absf(dy) + absf(dx);
            let near_edge = le_tile(
                absf(q - cutoff),
                epsilon * (one64 + radius_l1 * radius_l1 * precision_l1),
            );
            edge = select(near_edge, broadcast_scalar(1i32, shape![1, 1, 128]), edge);
            let exponent: Tile<f32, { [1, 1, 128] }> = convert_tile(q * minus_half);
            let amplitude: Tile<f32, { [1, 1, 128] }> = convert_tile(amplitude64);
            let value = amplitude * exp(exponent);
            sum = sum
                + select(
                    le_tile(q, broadcast_scalar(truncate_squared, shape![1, 1, 128])),
                    value,
                    zero,
                );
        }
        let clipped = select(
            gt_tile(sum, broadcast_scalar(1.0f32, shape![1, 1, 128])),
            broadcast_scalar(1.0f32, shape![1, 1, 128]),
            sum,
        );
        output.store(clipped);
        boundary.store(edge);
    }
}

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    version: u32,
    shape: [usize; 3],
    counts: Vec<usize>,
    repeats: usize,
}

fn validate(request: &Request, packed: &[f64]) -> Result<(usize, usize, usize)> {
    let batch = request.counts.len();
    if request.version != 1
        || !(1..=64).contains(&batch)
        || request.shape.iter().any(|&d| !(1..=4096).contains(&d))
        || request.counts.iter().any(|&g| g > 10_000)
        || request.repeats > 1000
    {
        return Err(
            "Unsupported version, dimensions, batch, Gaussian count or repeat count".into(),
        );
    }
    let pixels = request.shape.iter().product::<usize>();
    if pixels * batch > 128 * 1024 * 1024 {
        return Err("Output exceeds 128M-voxel safety limit".into());
    }
    let max_g = request.counts.iter().copied().max().unwrap().max(1);
    if packed.len() != batch * max_g * 16 || packed.iter().any(|x| !x.is_finite()) {
        return Err("Invalid Gaussian payload length or nonfinite values".into());
    }
    for (b, &count) in request.counts.iter().enumerate() {
        for g in 0..count {
            let row = &packed[(b * max_g + g) * 16..(b * max_g + g + 1) * 16];
            let p = &row[3..12];
            let det = p[0] * (p[4] * p[8] - p[5] * p[7]) - p[1] * (p[3] * p[8] - p[5] * p[6])
                + p[2] * (p[3] * p[7] - p[4] * p[6]);
            let norm = p.iter().map(|x| x.abs()).sum::<f64>();
            if row[..3].iter().any(|x| x.abs() > 1e6)
                || p.iter().any(|x| x.abs() > 1e12)
                || row[12] < 0.0
                || row[12] > 1e6
                || (row[13] - norm).abs() > 1e-12 * norm.max(1.0)
                || p[0] <= 0.0
                || p[0] * p[4] - p[1] * p[3] <= 0.0
                || det <= 0.0
                || (p[1] - p[3]).abs() > 1e-12 * norm.max(1.0)
                || (p[2] - p[6]).abs() > 1e-12 * norm.max(1.0)
                || (p[5] - p[7]).abs() > 1e-12 * norm.max(1.0)
            {
                return Err(
                    "Gaussian geometry/precision/amplitude outside validated domain".into(),
                );
            }
        }
    }
    Ok((pixels, max_g, pixels.div_ceil(8192) * 8192))
}

fn read_request(path: &str) -> Result<(Request, Vec<f64>)> {
    let mut file = fs::File::open(path)?;
    if file.metadata()?.len() > 128 * 1024 * 1024 {
        return Err("Input exceeds 128MiB safety limit".into());
    }
    let mut prefix = [0u8; 12];
    file.read_exact(&mut prefix)?;
    if &prefix[..8] != b"PHOTON01" {
        return Err("Invalid input magic".into());
    }
    let size = u32::from_le_bytes(prefix[8..].try_into()?) as usize;
    if size == 0 || size > 65536 {
        return Err("Invalid header size".into());
    }
    let mut header = vec![0u8; size];
    file.read_exact(&mut header)?;
    let request: Request = serde_json::from_slice(&header)?;
    let mut payload = Vec::new();
    file.read_to_end(&mut payload)?;
    if payload.len() % 8 != 0 {
        return Err("Incomplete f64 payload".into());
    }
    let packed: Vec<f64> = payload
        .chunks_exact(8)
        .map(|v| f64::from_le_bytes(v.try_into().unwrap()))
        .collect();
    validate(&request, &packed)?;
    Ok((request, packed))
}

fn memory_info() -> Result<(usize, usize)> {
    let (mut free, mut total) = (0usize, 0usize);
    // Device::new has made the context current; these are valid host out-pointers.
    unsafe {
        cuda_core::sys::cuMemGetInfo_v2(&mut free, &mut total).result()?;
    }
    Ok((free, total))
}

struct Runtime {
    device: Arc<Device>,
    stream: Arc<cuda_core::Stream>,
    context_ms: f64,
}

impl Runtime {
    fn new() -> Result<Self> {
        let start = Instant::now();
        let device = Device::new(0)?;
        let stream = device.new_stream()?;
        enable_cache()?;
        Ok(Self {
            device,
            stream,
            context_ms: start.elapsed().as_secs_f64() * 1000.0,
        })
    }
}

fn execute(input: &str, output_path: &str, runtime: &Runtime) -> Result<serde_json::Value> {
    let total_start = Instant::now();
    let (request, packed) = read_request(input)?;
    let parse_ms = total_start.elapsed().as_secs_f64() * 1000.0;
    let (pixels, max_g, padded) = validate(&request, &packed)?;
    let batch = request.counts.len();
    let device = &runtime.device;
    let stream = &runtime.stream;
    let device_name = device.name()?;
    let compiles_before = cutile::jit_cache::jit_backend_compile_count();
    let hits_before = cutile::jit_cache::jit_disk_hit_count();
    let memory_before = memory_info()?;
    let transfer_start = Instant::now();
    let input_bytes = packed.len() * 8 + batch * 4;
    let g = api::copy_host_vec_to_device(&Arc::new(packed))
        .sync_on(&stream)?
        .reshape(&[batch, max_g, 16])?;
    let counts = api::copy_host_vec_to_device(&Arc::new(
        request.counts.iter().map(|&n| n as i32).collect(),
    ))
    .sync_on(&stream)?;
    let h2d_wall_ms = transfer_start.elapsed().as_secs_f64() * 1000.0;
    let allocation_start = Instant::now();
    let mut output = api::zeros::<f32>(&[batch, padded / 8192, 8192]).sync_on(&stream)?;
    let mut boundary = api::zeros::<i32>(&[batch, padded / 8192, 8192]).sync_on(&stream)?;
    let output_allocation_ms = allocation_start.elapsed().as_secs_f64() * 1000.0;
    let compile_start = Instant::now();
    photon_kernel::render(
        (&mut output).partition([1, 1, 128]),
        (&mut boundary).partition([1, 1, 128]),
        &g,
        &counts,
        request.shape[1] as i32,
        request.shape[2] as i32,
        pixels as i32,
        16.0,
    )
    .compile_on(&stream)?;
    let jit_prepare_wall_ms = compile_start.elapsed().as_secs_f64() * 1000.0;
    let first_start = Instant::now();
    photon_kernel::render(
        (&mut output).partition([1, 1, 128]),
        (&mut boundary).partition([1, 1, 128]),
        &g,
        &counts,
        request.shape[1] as i32,
        request.shape[2] as i32,
        pixels as i32,
        16.0,
    )
    .sync_on(&stream)?;
    let first_launch_wall_ms = first_start.elapsed().as_secs_f64() * 1000.0;
    let mut graph_capture_ms = 0.0;
    let mut event_ms = Vec::new();
    let mut host_ms = Vec::new();
    if request.repeats > 0 {
        let capture_start = Instant::now();
        let graph = CudaGraph::scope(&stream, |s| {
            s.record(photon_kernel::render(
                (&mut output).partition([1, 1, 128]),
                (&mut boundary).partition([1, 1, 128]),
                &g,
                &counts,
                request.shape[1] as i32,
                request.shape[2] as i32,
                pixels as i32,
                16.0,
            ))?;
            Ok(())
        })?;
        graph_capture_ms = capture_start.elapsed().as_secs_f64() * 1000.0;
        graph.launch().sync_on(&stream)?;
        let start_event = device.new_event()?;
        let end_event = device.new_event()?;
        for _ in 0..request.repeats {
            let host_start = Instant::now();
            start_event.record(&stream)?;
            // Graph/buffers remain alive until completion; no conflicting access.
            unsafe {
                graph.launch().async_on(&stream)?;
            }
            end_event.record(&stream)?;
            end_event.synchronize()?;
            event_ms.push(start_event.elapsed_time(&end_event)?);
            host_ms.push(host_start.elapsed().as_secs_f64() * 1000.0);
        }
    }
    let transfer_start = Instant::now();
    let values = output.to_host_vec().sync_on(&stream)?;
    let flags = boundary.to_host_vec().sync_on(&stream)?;
    let d2h_wall_ms = transfer_start.elapsed().as_secs_f64() * 1000.0;
    let memory_after = memory_info()?;
    let metadata = json!({"version":1,"backend":"cuda-rust","device":device_name,"shape":request.shape,
        "batch":batch,"pixels_per_scene":pixels,"input_device_bytes":input_bytes,"output_device_bytes":batch*padded*8,
        "device_free_bytes_before":memory_before.0,"device_free_bytes_after":memory_after.0,"device_total_bytes":memory_after.1,
        "parse_ms":parse_ms,"context_ms":runtime.context_ms,"h2d_wall_ms":h2d_wall_ms,"output_allocation_ms":output_allocation_ms,
        "jit_prepare_wall_ms":jit_prepare_wall_ms,"first_launch_after_compile_wall_ms":first_launch_wall_ms,"graph_capture_ms":graph_capture_ms,
        "warm_cuda_event_ms":event_ms,"warm_host_dispatch_and_sync_ms":host_ms,"d2h_wall_ms":d2h_wall_ms,
        "jit_backend_compiles":cutile::jit_cache::jit_backend_compile_count()-compiles_before,"jit_disk_hits":cutile::jit_cache::jit_disk_hit_count()-hits_before,
        "native_compute_pipeline_ms":total_start.elapsed().as_secs_f64()*1000.0,
        "timing_note":"CUDA events bracket warmed single-kernel graph replay; includes any host enqueue gaps; excludes transfers, JIT, context and graph capture"});
    let mut metadata = metadata;
    let write_start = Instant::now();
    let header = serde_json::to_vec(&metadata)?;
    // DrvFS makes thousands of default 8KiB writes expensive for 3D volumes.
    let capacity = if std::env::var_os("PHOTON_GPU_SMALL_WRITES").is_some() {
        8192
    } else {
        1024 * 1024
    };
    let mut file = std::io::BufWriter::with_capacity(capacity, fs::File::create(output_path)?);
    file.write_all(b"PHOTOUT1")?;
    file.write_all(&(header.len() as u32).to_le_bytes())?;
    file.write_all(&header)?;
    for b in 0..batch {
        for value in &values[b * padded..b * padded + pixels] {
            file.write_all(&value.to_le_bytes())?;
        }
    }
    for b in 0..batch {
        for flag in &flags[b * padded..b * padded + pixels] {
            file.write_all(&[u8::from(*flag != 0)])?;
        }
    }
    file.flush()?;
    metadata["output_write_ms"] = json!(write_start.elapsed().as_secs_f64() * 1000.0);
    metadata["native_request_wall_ms"] = json!(total_start.elapsed().as_secs_f64() * 1000.0);
    metadata["output_buffer_bytes"] = json!(capacity);
    Ok(metadata)
}

fn enable_cache() -> Result<()> {
    let cache = if let Ok(namespace) = std::env::var("PHOTON_GPU_CACHE_NAMESPACE") {
        if namespace.is_empty()
            || !namespace
                .chars()
                .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
        {
            return Err("Invalid cache namespace".into());
        }
        cutile::jit_cache::FileSystemJitStore::new(
            std::path::PathBuf::from(std::env::var("HOME")?)
                .join(".cache/photon-gpu")
                .join(namespace),
        )?
    } else {
        cutile::jit_cache::FileSystemJitStore::default_location()?
    };
    cutile::jit_cache::enable(Arc::new(cache));
    Ok(())
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Job {
    input: String,
    output: String,
}

fn run() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() == 2 && args[1] == "--ping" {
        println!("PHOTON_GPU_OK");
        return Ok(());
    }
    if args.len() == 2 && args[1] == "--worker" {
        let runtime = Runtime::new()?;
        println!("{}", json!({"ready":true,"context_ms":runtime.context_ms}));
        std::io::stdout().flush()?;
        let mut input = std::io::stdin().lock();
        loop {
            // Bound control messages; bulk data stays in validated binary files.
            let mut line = String::new();
            let n = input.by_ref().take(16385).read_line(&mut line)?;
            if n == 0 {
                break;
            }
            if n > 16384 || !line.ends_with('\n') {
                return Err("Invalid worker message length".into());
            }
            let result = serde_json::from_str::<Job>(&line)
                .map_err(Into::into)
                .and_then(|job| execute(&job.input, &job.output, &runtime));
            match result {
                Ok(metadata) => println!("{}", json!({"ok":true,"metadata":metadata})),
                Err(error) => {
                    println!("{}", json!({"ok":false,"error":error.to_string()}));
                    std::io::stdout().flush()?;
                    return Err(error);
                }
            }
            std::io::stdout().flush()?;
        }
        return Ok(());
    }
    if args.len() != 3 {
        return Err("Usage: photon-gpu INPUT.bin OUTPUT.bin | --worker | --ping".into());
    }
    // Reject malformed requests before initializing CUDA, including one-shot mode.
    read_request(&args[1])?;
    let runtime = Runtime::new()?;
    println!("{}", execute(&args[1], &args[2], &runtime)?);
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("photon-gpu: {error}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn invalid_requests_rejected_before_cuda() {
        let mut r = Request {
            version: 1,
            shape: [1, 8, 8],
            counts: vec![0],
            repeats: 3,
        };
        assert!(validate(&r, &[0.0; 16]).is_ok());
        r.counts = vec![10001];
        assert!(validate(&r, &[]).is_err());
        r.counts = vec![0];
        r.shape = [4096; 3];
        assert!(validate(&r, &[0.0; 16]).is_err());
        r.shape = [1, 8, 8];
        r.repeats = 1001;
        assert!(validate(&r, &[0.0; 16]).is_err());
        r.repeats = 3;
        let mut data = [0.0; 16];
        data[1] = f64::NAN;
        assert!(validate(&r, &data).is_err());
    }
}
