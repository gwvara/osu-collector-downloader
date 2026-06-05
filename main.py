"""
osu! Beatmap Collection Downloader
===================================
Download beatmaps from osu!Collector collections automatically.
Uses mirror servers (Nerinyan, catboy.best) for fast, no-login downloads.
Always downloads WITHOUT video to save bandwidth and storage.

Usage:
    python main.py
    
Then follow the interactive prompts.
"""

import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.prompt import Prompt
from rich.rule import Rule

from utils import parse_collection_url, find_osu_songs_dir, format_size, format_duration
from collector import fetch_collection
from downloader import download_beatmaps

console = Console()

BANNER = r"""[bold magenta]
   ██████╗ ███████╗██╗   ██╗██╗
  ██╔═══██╗██╔════╝██║   ██║██║
  ██║   ██║███████╗██║   ██║██║
  ██║   ██║╚════██║██║   ██║╚═╝
  ╚██████╔╝███████║╚██████╔╝██╗
   ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝[/]
[bold cyan]  Beatmap Collection Downloader[/]
[dim]  Download from osu!Collector • No login required[/]
[dim]  Powered by Nerinyan & catboy.best mirrors[/]
"""


def show_step(number: int, text: str):
    """Display a step header."""
    console.print()
    console.print(f"  [bold yellow]Step {number}[/] [bold white]│[/] [bold]{text}[/]")
    console.print()


def main():
    console.clear()
    console.print(BANNER)
    console.print(Rule(style="dim"))

    # ─── Step 1: Collection URL ───────────────────────────────────────
    show_step(1, "📋 Masukkan URL Collection")
    console.print("  [dim]Format: https://osucollector.com/collections/xxxxx/nama-collection[/]")
    console.print("  [dim]Atau cukup masukkan ID collection (contoh: 21770)[/]")
    console.print()

    url = Prompt.ask("  [bold cyan]🔗 Collection URL/ID")
    collection_id = parse_collection_url(url)

    if collection_id is None:
        console.print()
        console.print("  [bold red]❌ URL/ID tidak valid![/]")
        console.print("  [dim]Pastikan formatnya benar, contoh:[/]")
        console.print("  [dim]  https://osucollector.com/collections/21770/CARBONE'S-AIM-COLLECTION[/]")
        input("\n  Tekan Enter untuk keluar...")
        sys.exit(1)

    # ─── Step 2: Fetch Collection ─────────────────────────────────────
    show_step(2, "🔍 Mengambil Data Collection")

    with console.status("  [cyan]Menghubungi osucollector.com...", spinner="dots"):
        try:
            collection = fetch_collection(collection_id)
        except Exception as e:
            console.print(f"  [bold red]❌ Gagal mengambil data: {e}[/]")
            input("\n  Tekan Enter untuk keluar...")
            sys.exit(1)

    # Display collection info
    info_table = Table(
        box=box.ROUNDED,
        border_style="bright_cyan",
        show_header=False,
        padding=(0, 2),
        min_width=50,
    )
    info_table.add_column("Key", style="bold white", min_width=18)
    info_table.add_column("Value", style="bright_green")

    info_table.add_row("🎵 Collection", collection['name'])
    info_table.add_row("👤 Uploader", collection['uploader'])
    info_table.add_row("📦 Beatmapsets", str(collection['beatmapset_count']))
    info_table.add_row("🎯 Total Beatmaps", str(collection['beatmap_count']))
    info_table.add_row("⭐ Favourites", str(collection['favourites']))

    console.print(Panel(
        info_table,
        title="[bold cyan]Collection Info[/]",
        border_style="cyan",
        padding=(1, 1),
    ))

    total_sets = collection['beatmapset_count']
    if total_sets == 0:
        console.print("  [bold red]❌ Collection ini kosong![/]")
        input("\n  Tekan Enter untuk keluar...")
        sys.exit(1)

    # ─── Step 3: Download Count ───────────────────────────────────────
    show_step(3, f"📥 Pilih Jumlah Download (tersedia: {total_sets})")
    console.print("  [dim]Ketik angka (1-{}) atau 'all' untuk semua[/]".format(total_sets))
    console.print()

    while True:
        count_input = Prompt.ask(
            "  [bold cyan]📊 Jumlah beatmapset",
            default="all"
        )
        if count_input.strip().lower() == 'all':
            download_count = total_sets
            break
        try:
            download_count = int(count_input)
            if 1 <= download_count <= total_sets:
                break
            console.print(f"  [red]⚠ Masukkan angka antara 1 dan {total_sets}![/]")
        except ValueError:
            console.print("  [red]⚠ Masukkan angka yang valid atau 'all'![/]")

    # ─── Step 4: Output Directory ─────────────────────────────────────
    show_step(4, "📁 Folder Tujuan Download")

    songs_dir = find_osu_songs_dir()
    output_dir = None

    if songs_dir:
        console.print(f"  [green]✅ Folder osu! Songs ditemukan:[/]")
        console.print(f"  [bold white]{songs_dir}[/]")
        console.print()
        use_default = Prompt.ask(
            "  [bold cyan]Gunakan folder ini?",
            choices=["y", "n"],
            default="y"
        )
        if use_default.lower() == 'y':
            output_dir = songs_dir
    
    if output_dir is None:
        if not songs_dir:
            console.print("  [yellow]⚠ Folder osu! Songs tidak ditemukan otomatis[/]")
        console.print()
        custom = Prompt.ask("  [bold cyan]📂 Masukkan path folder tujuan")
        output_dir = Path(custom.strip().strip('"').strip("'"))

    # Create directory if needed
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        console.print(f"  [bold red]❌ Gagal membuat folder: {e}[/]")
        input("\n  Tekan Enter untuk keluar...")
        sys.exit(1)

    # ─── Step 5: Configuration ────────────────────────────────────────
    show_step(5, "⚙️  Konfigurasi Download")
    console.print("  [dim]Download paralel: berapa file sekaligus (1-5, default: 3)[/]")
    console.print()

    max_concurrent = 3
    try:
        c_input = Prompt.ask("  [bold cyan]🔀 Download paralel", default="3")
        max_concurrent = max(1, min(5, int(c_input)))
    except ValueError:
        max_concurrent = 3

    # ─── Confirmation ─────────────────────────────────────────────────
    console.print()
    console.print(Rule("[bold magenta] Konfirmasi Download ", style="magenta"))
    console.print()

    confirm_table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="magenta",
        show_header=False,
        padding=(0, 2),
        min_width=55,
    )
    confirm_table.add_column("Setting", style="bold white", min_width=20)
    confirm_table.add_column("Value", style="bright_cyan")

    confirm_table.add_row("🎵 Collection", collection['name'])
    confirm_table.add_row("📥 Jumlah Download", f"{download_count} beatmapsets")
    confirm_table.add_row("📁 Folder Tujuan", str(output_dir))
    confirm_table.add_row("🔀 Paralel", f"{max_concurrent} download")
    confirm_table.add_row("🚫 Video", "Tanpa Video (No Video)")
    confirm_table.add_row("🔄 Mirror", "Nerinyan → catboy.best")
    confirm_table.add_row("🔁 Retry", "3x per mirror")

    console.print(confirm_table)
    console.print()

    confirm = Prompt.ask(
        "  [bold yellow]🚀 Mulai download?",
        choices=["y", "n"],
        default="y"
    )
    if confirm.lower() != 'y':
        console.print("  [dim]Download dibatalkan.[/]")
        input("\n  Tekan Enter untuk keluar...")
        sys.exit(0)

    # ─── Step 6: Download ─────────────────────────────────────────────
    console.print()
    console.print(Rule("[bold green] Download Dimulai ", style="green"))
    console.print()

    beatmapset_ids = collection['beatmapsets'][:download_count]
    start_time = time.time()

    results = download_beatmaps(
        beatmapset_ids,
        output_dir,
        max_concurrent=max_concurrent,
    )

    elapsed = time.time() - start_time

    # ─── Step 7: Results ──────────────────────────────────────────────
    console.print()
    console.print(Rule("[bold cyan] Hasil Download ", style="cyan"))
    console.print()

    success_count = len(results['success'])
    skipped_count = len(results['skipped'])
    failed_count = len(results['failed'])

    result_text = []
    result_text.append(f"[bold green]  ✅ Berhasil    : {success_count} beatmapsets[/]")
    if skipped_count > 0:
        result_text.append(f"[bold yellow]  ⏭️  Dilewati    : {skipped_count} beatmapsets (sudah ada)[/]")
    if failed_count > 0:
        result_text.append(f"[bold red]  ❌ Gagal       : {failed_count} beatmapsets[/]")
    result_text.append(f"[bold cyan]  📦 Total Ukuran: {format_size(results['total_size'])}[/]")
    result_text.append(f"[bold white]  ⏱️  Waktu       : {format_duration(elapsed)}[/]")
    result_text.append(f"[bold white]  📁 Lokasi      : {output_dir}[/]")

    console.print(Panel(
        "\n".join(result_text),
        title="[bold green]📊 Ringkasan[/]",
        border_style="green",
        padding=(1, 1),
    ))

    # Show failed downloads
    if results['failed']:
        console.print()
        console.print("  [bold red]Beatmapsets yang gagal:[/]")
        # Show max 20 failures
        show_failures = results['failed'][:20]
        for fail in show_failures:
            console.print(f"    [red]• ID {fail['id']}: {fail.get('message', 'Unknown error')}[/]")
        if len(results['failed']) > 20:
            console.print(f"    [dim]... dan {len(results['failed']) - 20} lainnya[/]")

    # Final message
    console.print()
    if success_count > 0:
        console.print(Panel(
            "[bold bright_magenta]🎮 Selamat bermain osu![/]\n"
            "[dim]File .osz akan otomatis diimport saat kamu membuka osu![/]\n"
            "[dim]Cukup buka osu! dan beatmap baru akan muncul.[/]",
            border_style="magenta",
            padding=(1, 2),
        ))
    
    console.print()
    input("  Tekan Enter untuk keluar...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n  [yellow]Download dihentikan oleh user.[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n  [bold red]Error tak terduga: {e}[/]")
        input("\n  Tekan Enter untuk keluar...")
        sys.exit(1)
