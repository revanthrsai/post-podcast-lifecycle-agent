import os
import re
import json
import asyncio
import argparse
from typing import Any, Dict, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from config import Config
from memory.session_store import SessionStore

# Calling Agents
from agents.transcription_agent import build_transcription_agent
from agents.research_agent import build_research_agent
from agents.outline_agent import build_outline_agent
from agents.show_notes_agent import build_show_notes_agent
from agents.timestamp_agent import build_timestamp_agent
from agents.quote_agent import build_quote_agent
from agents.social_agent import build_social_agent
from agents.seo_agent import build_seo_agent

# Agent Schemas
try:
    from agents.schemas import (
        TranscriptionOutput,
        ResearchOutput,
        OutlineOutput,
        ShowNotesOutput,
        TimestampOutput,
        QuotesOutput,
        SocialOutput,
        SEOOutput,
    )
except Exception as e:
    # Schema validation will be disabled if import fails
    console = Console()
    console.print(f"[yellow]⚠️  Schema validation disabled: {e}[/yellow]")
    TranscriptionOutput = ResearchOutput = OutlineOutput = ShowNotesOutput = None
    TimestampOutput = QuotesOutput = SocialOutput = SEOOutput = None

console = Console()

# Orchestrates the multi-agent podcast automation pipeline.
class PodcastOrchestrator:

    # Configuration constants
    TRANSCRIPT_SAMPLE_LENGTH = 15000
    MAX_RETRIES = 3
    BACKOFF_BASE = 5

    # Initializes directory structure, session and all agents.
    def __init__(self, session_id: str = "pod_001"):
        
        # directory  
        self.output_dir = Config.OUTPUT_DIR
        self.raw_dir = os.path.join(self.output_dir, "agents_rawdata")
        
        # Create subdirectory if they don't exist
        os.makedirs(self.raw_dir, exist_ok=True)

        # Session
        self.store = SessionStore(session_id=session_id)
        self.session_service = InMemorySessionService()
        self.session = None
        self.session_id = session_id

        # Agent Initialization
        self.transcriber = build_transcription_agent()
        self.researcher = build_research_agent()
        self.outliner = build_outline_agent()
        self.show_notes = build_show_notes_agent()
        self.timestamp_agent = build_timestamp_agent()
        self.quote_agent = build_quote_agent()
        self.social_agent = build_social_agent()
        self.seo_agent = build_seo_agent()

    # Helper methods
    
    async def _ensure_session(self):
        if not self.session:
            # Generate user ID from session ID or environment variable
            user_id = os.environ.get("USER_ID", f"user_{self.session_id}")
            
            # Create session with Google ADK
            self.session = await self.session_service.create_session(app_name="PodcastAutomator", user_id=user_id)

    # save agent outputs
    def _write_json(self, path: str, data: Any):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    # save only JSON and avoid functional texts
    def _extract_first_json(self, text: str) -> Dict[str, Any]:
        markdown_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if markdown_match:
            try:
                return json.loads(markdown_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Regex pattern for balanced JSON with nesting
        match = re.search(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", text, re.DOTALL)
        
        if not match:
            # No JSON pattern found
            raise ValueError(
                f"No JSON object found in agent output.\n"
                f"Preview (first 200 chars): {text[:200]}"
            )
        
        # Extract the matched JSON string
        json_str = match.group(0)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Parsing failed
            raise ValueError(
                f"JSON parse error: {e}\n"
                f"Extracted JSON preview (first 300 chars): {json_str[:300]}"
            )
        
    # ----------------------------------------------------------- CORE EXECUTION ----------------------------------------------------------

    async def _run_agent(self, agent, prompt: str,raw_filename: str,expected_schema: Optional[Any] = None,max_retries: Optional[int] = None,) -> Dict[str, Any]:
        # Ensure session exists before running agent
        await self._ensure_session()

        max_retries = max_retries or self.MAX_RETRIES
        
        attempt = 0

        while attempt < max_retries:
            attempt += 1
            
            try:
                # Create a fresh Runner for this agent call
                runner = Runner(agent=agent, app_name="PodcastAutomator", session_service=self.session_service)

                # Construct user message
                message = types.Content(role="user", parts=[types.Part(text=prompt)])
                
                # Stream the prompt response and concatenate text chunks
                final_text = ""
                async for event in runner.run_async(session_id=self.session.id, user_id=self.session.user_id, new_message=message):
                    # Extract text from response events
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if getattr(part, "text", None):
                                final_text += part.text

                # Save complete agent response for debugging
                raw_path = os.path.join(self.raw_dir, raw_filename)
                with open(raw_path, "w", encoding="utf-8") as fh:
                    fh.write(final_text)

                # Agent may use tools without returning text
                if not final_text or final_text.strip() == "":
                    return {"status": "tool_used"}

                # Extract JSON
                parsed = self._extract_first_json(final_text)

                # Validate schema structure
                if expected_schema:
                    expected_schema.parse_obj(parsed)

                # Success
                return parsed

            except Exception as e:
                err = str(e)
                
                # API errors 
                rate_limit_indicators = [
                    "429",                  # HTTP 429 Too Many Requests
                    "RESOURCE_EXHAUSTED",   # gRPC status code
                    "Rate limit",           # Error message text
                    "quota"                 # Quota exceeded messages
                ]
                
                if any(indicator in err for indicator in rate_limit_indicators):
                    # exponential backoff: 5s, 10s, 15s
                    wait = self.BACKOFF_BASE * attempt
                    console.print(
                        f"[yellow]Transient error (rate limit); "
                        f"backing off {wait}s (attempt {attempt}/{max_retries})[/yellow]"
                    )
                    await asyncio.sleep(wait)
                    continue

                # Retry on parsing errors
                parsing_error_indicators = ["JSON", "parse", "Schema", "validation"]
                
                if attempt == 1 and any(
                    indicator in err for indicator in parsing_error_indicators
                ):
                    console.print(
                        "[yellow]Parsing/validation failed — "
                        "retrying with JSON-only instruction.[/yellow]"
                    )
                    # Add clarification
                    prompt = (
                        f"{prompt}\n\n"
                        "IMPORTANT: Return ONLY the JSON object with no extra text, "
                        "preambles, or markdown formatting."
                    )
                    continue

                # Errors
                console.print(f"[red]Permanent error running agent: {err}[/red]")
                raise

        # Max Retires Exceeded
        raise RuntimeError(
            f"Agent failed after {max_retries} attempts. "
            f"Check {os.path.join(self.raw_dir, raw_filename)} for details."
        )

    # ----------------------------------------------------------- MAIN PIPELINE ----------------------------------------------------------

    async def run_lifecycle(self, topic: str = "General Podcast", audio_path: Optional[str] = None, transcript_path: Optional[str] = None):
        # Progress indicator
        with Progress(
            SpinnerColumn(), 
            TextColumn("[progress.description]{task.description}")
        ) as progress:
            
            task = progress.add_task("Starting podcast automation...", total=None)
            
            try:
                # STAGE 1: INGEST (SEQUENTIAL)
                progress.update(task, description="Ingest: preparing transcript...")
                transcript_text = ""

                # Priority 1: Transcribe audio file
                if audio_path and os.path.exists(audio_path):
                    from tools.audio_tool import transcribe_audio
                    
                    loop = asyncio.get_event_loop()
                    console.print("[cyan]Transcribing audio (this may take a while)...[/cyan]")
                    
                    # Run blocking transcription in executor to Keeps responsiveness
                    res = await loop.run_in_executor(None, lambda: transcribe_audio(audio_path))

                    # Validate transcription result
                    if not isinstance(res, dict) or not res.get("ok"):
                        error_msg = (
                            res.get("error", "unknown") 
                            if isinstance(res, dict) 
                            else str(res)
                        )
                        raise RuntimeError(f"Transcription failed: {error_msg}")

                    # Extract transcript and save
                    transcript_text = res["data"]["transcript"]
                    self.store.set("transcript", transcript_text)
                    self._write_json( os.path.join(self.output_dir, "transcription.json"), {"transcript": transcript_text})

                # Priority 2: Load transcript file
                elif transcript_path and os.path.exists(transcript_path):
                    from tools.custom_tools import read_transcript
                    
                    transcript_text = read_transcript(transcript_path)
                    self.store.set("transcript", transcript_text)
                    self._write_json(os.path.join(self.output_dir, "transcription.json"), {"transcript": transcript_text})

                # Priority 3: fallback
                else:
                    transcript_text = self.store.get("transcript") or "No transcript provided."
                    self.store.set("transcript", transcript_text)
                    self._write_json(os.path.join(self.output_dir, "transcription.json"), {"transcript": transcript_text})

                progress.update(task, description="Ingest completed.")

                ## STAGE 2: RESEARCH (SEQUENTIAL)

                progress.update(task, description="Researching topic...")
                research_prompt = f"Research this podcast topic: {topic}. Return JSON with fields: 'summary', 'bullets', 'citations'."
                research = await self._run_agent(self.researcher, research_prompt, "research_raw.json", expected_schema=ResearchOutput)
                self._write_json(os.path.join(self.output_dir, "research.json"), research)
                self.store.set("research", research)
                progress.update(task, description="Research done.")

                ### STAGE 3: OUTLINE (SEQUENTIAL)
                
                progress.update(task, description="Creating outline...")
                """ Use first N characters of transcript to avoid token limits"""
                transcript_sample = (self.store.get("transcript") or "")[:self.TRANSCRIPT_SAMPLE_LENGTH]
                outline_prompt = "Create a podcast outline using the research and transcript sample. Return JSON with fields: 'hook', 'segments', 'closing'."
                outline = await self._run_agent(self.outliner, outline_prompt, "outline_raw.json", expected_schema=OutlineOutput)
                self._write_json(os.path.join(self.output_dir, "outline.json"), outline)
                self.store.set("outline", outline)
                
                progress.update(task, description="Outline done.")

                #### STAGE 4: Output Content Bundle Generation (PARALLEL)
                progress.update(task, description="Generating assets (parallel)...")

                async def run_and_save(agent, prompt, raw_name, out_name, schema):
                    output = await self._run_agent(agent, prompt, raw_name, expected_schema=schema)
                    self._write_json(os.path.join(self.output_dir, out_name), output)
                    return output

                # Create parallel tasks for all asset agents
                tasks = [
                    asyncio.create_task(run_and_save(self.show_notes, "Write comprehensive show notes in JSON format.", "show_notes_raw.json", "show_notes.json", ShowNotesOutput)),
                    asyncio.create_task(run_and_save(self.timestamp_agent, "Generate exactly 8 chapter timestamps with descriptions (JSON).", "timestamps_raw.json", "timestamps.json", TimestampOutput)),
                    asyncio.create_task(run_and_save(self.quote_agent, "Extract 5 memorable and shareable quotes (JSON).", "quotes_raw.json", "quotes.json", QuotesOutput)),
                    asyncio.create_task(run_and_save(self.social_agent, "Create social media posts: twitter_thread, linkedin_posts, instagram_captions (JSON).", "social_raw.json", "social.json", SocialOutput)),
                    asyncio.create_task(run_and_save(self.seo_agent, "Generate SEO metadata: title, meta_description, keywords (JSON).", "seo_raw.json", "seo.json", SEOOutput)),
                ]


                # Execute all tasks in parallel
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Report failures but continue pipeline
                failed_count = 0
                for idx, res in enumerate(results):
                    if isinstance(res, Exception):
                        failed_count += 1
                        console.print(
                            f"[red]Asset task #{idx} failed: {res}[/red]"
                        )
                
                if failed_count > 0:
                    console.print(f"[yellow]⚠️  {failed_count} asset(s) failed, Check raw outputs for details.[/yellow]")

                progress.update(task, description="Content Bundle generation completed.")

                # STAGE 5: SAVE CONTEXT & SNAPSHOTS
                context = {
                    "topic": topic,
                    "transcript": self.store.get("transcript"),
                    "research": self.store.get("research"),
                    "outline": self.store.get("outline"),
                }
                self._write_json(os.path.join(self.raw_dir, "context.json"), context)

                if hasattr(self.store, "snapshot") and callable(getattr(self.store, "snapshot")):
                    self._write_json(os.path.join(self.raw_dir, "session_snapshot.json"), self.store.snapshot())

                # GOOD TO GO
                progress.update(task, description="Finalizing...")
                
                console.print("[bold green]✅ Podcast Lifecycle Completed![/bold green]")
                console.print(f"Final JSON outputs: {self.output_dir}")
                console.print(f"Raw agent traces: {self.raw_dir}")

            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️  Pipeline interrupted by user[/yellow]")
                raise
                
            except Exception as e:
                console.print(f"[bold red]❌ CRITICAL ERROR[/bold red] {e}")
                raise


# ENTRY POINT
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Podcast Orchestrator - Direct execution mode")
    p = argparse.ArgumentParser()
    p.add_argument("--topic", default="General Podcast", help="Episode topic/title")
    p.add_argument("--audio", default=None, help="Path to audio file (optional)")
    p.add_argument("--transcript", default=None, help="Path to transcript file (optional)")
    args = p.parse_args()

    orchestrator = PodcastOrchestrator()
    try:
        asyncio.run(orchestrator.run_lifecycle(topic=args.topic, audio_path=args.audio, transcript_path=args.transcript))
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted by user[/red]")