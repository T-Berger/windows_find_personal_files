use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::PathBuf;

use clap::Parser;
use wpa_scan::{is_excluded, walk_roots_jsonl};

#[derive(Parser)]
#[command(name = "wpa-scan", about = "Fast filesystem walker for WPA")]
struct Args {
    /// Root directories to scan (e.g. C:\\ D:\\)
    #[arg(required = true)]
    roots: Vec<PathBuf>,

    /// File with one exclusion path prefix per line
    #[arg(long)]
    exclude_file: Option<PathBuf>,

    /// Output JSONL file (stdout if omitted)
    #[arg(long)]
    output: Option<PathBuf>,
}

fn load_exclusions(path: Option<PathBuf>) -> Result<Vec<String>, String> {
    match path {
        None => Ok(Vec::new()),
        Some(p) => {
            let content = std::fs::read_to_string(&p).map_err(|e| e.to_string())?;
            Ok(content
                .lines()
                .map(str::trim)
                .filter(|l| !l.is_empty() && !l.starts_with('#'))
                .map(String::from)
                .collect())
        }
    }
}

fn main() {
    let args = Args::parse();
    let exclusions = load_exclusions(args.exclude_file).unwrap_or_else(|e| {
        eprintln!("failed to load exclusions: {e}");
        std::process::exit(1);
    });

    let roots: Vec<PathBuf> = args
        .roots
        .into_iter()
        .filter(|r| r.exists() && !is_excluded(r, &exclusions))
        .collect();

    let count = match args.output {
        Some(path) => {
            let file = File::create(&path).unwrap_or_else(|e| {
                eprintln!("failed to create output: {e}");
                std::process::exit(1);
            });
            let mut writer = BufWriter::new(file);
            let n = walk_roots_jsonl(&roots, &exclusions, &mut writer).unwrap_or_else(|e| {
                eprintln!("walk failed: {e}");
                std::process::exit(1);
            });
            writer.flush().unwrap_or_else(|e| {
                eprintln!("flush failed: {e}");
                std::process::exit(1);
            });
            n
        }
        None => {
            let mut writer = BufWriter::new(std::io::stdout().lock());
            walk_roots_jsonl(&roots, &exclusions, &mut writer).unwrap_or_else(|e| {
                eprintln!("walk failed: {e}");
                std::process::exit(1);
            })
        }
    };

    eprintln!("wpa-scan: {count} files");
}
