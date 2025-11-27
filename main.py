import argparse
import asyncio
import os
import sys
import time
import subprocess
from rich import print
from orchestrator import PodcastOrchestrator


# Dashboard
def launch_dashboard():
    dashboard_script = os.path.join("dashboard", "dashboard_server.py")
    # Verify dashboard script exists
    if not os.path.exists(dashboard_script):
        print(f"[red]❌ Dashboard server not found at: {dashboard_script}[/red]")
        return None

    print("\n[cyan]🌐 Launching Dashboard at http://127.0.0.1:5000 ...[/cyan]\n")

    try:
        process = subprocess.Popen([sys.executable, dashboard_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give dashboard a moment
        time.sleep(2)
        
        # Check if Process already exited
        if process.poll() is not None:
            _, stderr = process.communicate()
            print(f"[red]❌ Dashboard crashed on startup: {stderr.decode()}[/red]")
            return None
        else:
            print("[green]✓ Dashboard server started successfully![/green]")
            return process
            
    except Exception as e:
        print(f"[red]❌ Failed to launch Dashboard: {e}[/red]")
        return None

# Arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="🎙️ Post-Podcast Lifecycle Automator (AI Multi-Agent Pipeline)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With explicit audio file
  python main.py --topic "AI in Healthcare" --audio "recordings/episode1.mp3"
  
  # With explicit transcript
  python main.py --topic "AI in Healthcare" --transcript "transcripts/episode1.txt"
  
  # Auto-detect from directories
  python main.py --topic "AI in Healthcare"
        """
    )

    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Topic or title of the podcast episode",
    )

    parser.add_argument(
        "--audio",
        type=str,
        default=None,
        help="Path to audio file (supports .mp3, .wav, .m4a)"
    )
    
    parser.add_argument(
        "--transcript",
        type=str,
        default=None,
        help="Path to transcript text file (.txt)"
    )

    return parser.parse_args()

# File Detection
def detect_inputs(args):
    """
    Priority Order:
      1. Explicit audio file (--audio flag)
      2. Auto-detect audio in podcast_recordings/
      3. Explicit transcript file (--transcript flag)
      4. Auto-detect transcript in test_data/
      5. Exit with code 1 if nothing found

    """
    # PRIORITY 1: Explicit Audio File
    if args.audio:
        if not os.path.exists(args.audio):
            print(f"[red]❌ Audio file not found: {args.audio}[/red]")
            sys.exit(1)
            
        if not args.audio.lower().endswith((".mp3", ".wav", ".m4a")):
            print(f"[yellow]⚠️  Warning: Unusual audio format. Supported: .mp3, .wav, .m4a[/yellow]")
        
        return args.audio, None

    # PRIORITY 2: Auto-Detect Audio File 
    recordings_dir = "podcast_recordings"
    if os.path.exists(recordings_dir):
        # Sort files for deterministic behavior across different filesystems
        files = sorted(os.listdir(recordings_dir))
        
        for f in files:
            if f.lower().endswith((".mp3", ".wav", ".m4a")):
                audio_path = os.path.join(recordings_dir, f)
                print(f"[cyan]🎧 Auto-detected audio file:[/cyan] {audio_path}")
                return audio_path, None

    # PRIORITY 3: Explicit Transcript File 
    if args.transcript:
        # Validate that the provided transcript file exists
        if not os.path.exists(args.transcript):
            print(f"[red]❌ Transcript file not found: {args.transcript}[/red]")
            sys.exit(1)
            
        return None, args.transcript

    # PRIORITY 4: Auto-Detect Transcript File
    transcript_dir = "test_data"
    if os.path.exists(transcript_dir):
        # Sort files for deterministic behavior
        files = sorted(os.listdir(transcript_dir))
        
        for f in files:
            if f.lower().endswith(".txt"):
                transcript_path = os.path.join(transcript_dir, f)
                print(f"[cyan]📄 Auto-detected transcript:[/cyan] {transcript_path}")
                return None, transcript_path

    # PRIORITY 5: No Valid Inputs Found
    print(
        "[red]❌ No podcast audio or transcript found.[/red]\n"
        "[yellow]Please either:[/yellow]\n"
        "  1. Provide --audio or --transcript flags\n"
        "  2. Add audio files to podcast_recordings/\n"
        "  3. Add transcript files to test_data/"
    )
    sys.exit(1)


def main():
    """
    Main Workflow:
      1. Parse command-line arguments
      2. Detect & validate input audio or transcript
      3. Run orchestrator
      4. Optionally launch dashboard for viewing output content bundle
    """
    print("[bold blue]🎙️ Post-Podcast Lifecycle Automator (Powered by Gemini / ADK)[/bold blue]")

    # Parse arguments
    args = parse_args()

    # Detect and validate inputs (audio or transcript)
    audio_path, transcript_path = detect_inputs(args)

    # Initialize the orchestrator
    orchestrator = PodcastOrchestrator()

    # Display configuration
    print(f"\n[bold cyan]📌 Topic:[/bold cyan] {args.topic}")
    if audio_path:
        print(f"[cyan]🎧 Using podcast audio file:[/cyan] {audio_path}")
    if transcript_path:
        print(f"[cyan]📄 Using podcast transcript file:[/cyan] {transcript_path}")

    # Run the multi-agent pipeline
    try:
        asyncio.run(
            orchestrator.run_lifecycle(
                topic=args.topic,
                audio_path=audio_path,
                transcript_path=transcript_path,
            )
        )
    except KeyboardInterrupt:
        print("\n[yellow]⚠️  Pipeline interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"\n[red]❌ Pipeline failed: {e}[/red]")
        sys.exit(1)
    
    # Ask user to launch dashboard
    print("\n" + "="*60)
    choice = input("Do you want to launch the dashboard now? (y/n): ").strip().lower()
    
    if choice in ("y", "yes"):
        dashboard_process = launch_dashboard()
        
        if dashboard_process:
            print("\n[bold cyan]📌 Dashboard is running at http://127.0.0.1:5000[/bold cyan]")
            print("[cyan]Visit dashboard to view your post podcast assets[/cyan]")
            print("[yellow]Press Ctrl+C to stop the dashboard and exit[/yellow]\n")
            
            try:
                # Keep running until user stops it
                dashboard_process.wait()
            except KeyboardInterrupt:
                print("\n[yellow]⚠️  Stopping dashboard...[/yellow]")
                dashboard_process.terminate()
                
                # Try graceful shutdown (5s)
                try:
                    dashboard_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # kill if it doesn't stop gracefully
                    dashboard_process.kill()
                    dashboard_process.wait()
                
                print("[green]✓ Dashboard stopped. Goodbye![/green]")
        else:
            print("\n[red]Failed to start dashboard. Check the error above.[/red]")
    else:
        print("\n[yellow]Skipping dashboard launch. Post-Podcast content bundle is ready in outputs/[/yellow]\n")


if __name__ == "__main__":
    main()