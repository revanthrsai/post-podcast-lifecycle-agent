# 🎙️ Post-Podcast Lifecycle Automator

> **Massive AI-powered transformation** over a traditionally time-consuming workflow

An intelligent multi-agent system built with **Google Agent Development Kit (ADK)** that automates the entire post-production workflow for podcast creators - from audio transcription to SEO-optimized content generation.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google)](https://github.com/google/adk)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)



---

## 📸

### 📈 Workflow
<img width="1536" height="1024" alt="pipeline-1" src="https://github.com/user-attachments/assets/4ccb7832-3cfd-418d-874b-efbf76f6d420" />


### 📟 Dashboard Interface
<img width="1365" height="671" alt="dashboard-LightMode" src="https://github.com/user-attachments/assets/fbe10c74-992b-44f8-beea-c74551c1cafd" />


---

## 🎯 The Problem

Podcast creators today face a problem in transforming raw audio into a complete content package which requires **hours of manual work** per episode, **Multiple disconnected flow** (transcription, editing, social media), **Different skill sets** (writing, SEO, social media), **Repetitive tasks**, **Inconsistent quality** across outputs and **Limited scalability** for growing channels. This results in delayed publishing, creator burnout, and missed monetization opportunities.

---

## ✨ The Solution

The **Post-Podcast Lifecycle Automator** provides an end-to-end AI automation pipeline that:

### 🚀 Key Features

| Feature                         | Benefit                                                      |
|---------------------------------|--------------------------------------------------------------|
| Automatic Transcription         | Converts audio to text using Google GenAI                    |
|  Smart Research                 | Gathers contextual background information                    |
|  Structured Outlining           | Creates episode structure with hooks and segments            |
|  Show Notes Generation          | Produces professional episode descriptions                   |
|  Timestamp Creation             | Generates chapter markers for YouTube/Spotify                |
|  Quote Extraction               | Identifies shareable, memorable quotes                       |
|  Social Media Content           | Creates Twitter threads, LinkedIn posts, Instagram captions  |
|  SEO Optimization               | Generates titles, meta descriptions, keywords                |
|  Parallel Processing            | Runs 5 content agents simultaneously                         |
|  Web Dashboard                  | Visual interface for reviewing all outputs                   |

### 📋 Architecture Highlights

- **Modular Multi-Agent System**: Each agent specializes in one task
- **Sequential → Parallel Optimization**: Research/outline run first, then 5 agents in parallel
- **Robust Error Handling**: Retry logic with exponential backoff for API rate limits
- **Clean Output Format**: All results saved as validated JSON files
- **Session Management**: Context persistence across agent calls

---

## 📚 Project Structure

```
podcast-lifecycle-automator/
│
├── 📄 .env                          
├── 📖 README.md                    
├── 📦 requirements.txt              
├── 🚀 main.py                      
├── ⚙️ config.py                     
├── 🎭 orchestrator.py              
│
├── 🤖 agents/                       
│   ├── transcription_agent.py     
│   ├── research_agent.py          
│   ├── outline_agent.py            
│   ├── show_notes_agent.py         
│   ├── timestamp_agent.py         
│   ├── quote_agent.py              
│   ├── social_agent.py            
│   ├── seo_agent.py               
│   └── schemas.py                  
│
├── 🛠️ tools/                      
│   ├── audio_tool.py              
│   ├── search_tool.py             
│   ├── custom_tools.py            
│   └── adk_tool_wrappers.py        
│
├── 🧠 memory/                      
│   └── session_store.py            
│
├── 📊 dashboard/                    
│   ├── dashboard_server.py        
│   └── templates/
│       └── dashboard.html         
│
├── 🎵 podcast_recordings/           
│   └── *.mp3                      
│
├── 📝 test_data/                    
│   └── sample_transcript.txt      
│
└── 📤 outputs/                     
    ├── transcription.json         
    ├── research.json               
    ├── outline.json                
    ├── show_notes.json             
    ├── timestamps.json            
    ├── quotes.json                 
    ├── social.json                 
    ├── seo.json                    
    └── agents_rawdata/             
         ├── *_raw.json             
         ├── context.json           
         └── session_snapshot.json  
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API key for Google AI Studio

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/revanthrsai/post-podcast-lifecycle-agent
```


### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=<your_gemini_api_key_here>
GOOGLE_PROJECT_ID=<your_google_cloud_project_id>
GOOGLE_LOCATION=asia-south1
MODEL_NAME=gemini-2.0-flash
```

> 💡 **Tip:** Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 4️⃣ Add Your Content

**Option A: Audio File**
- Place your podcast audio in `podcast_recordings/`
- Supported formats: `.mp3`, `.wav`, `.m4a`

**Option B: Transcript File**
- Place your transcript in `test_data/`
- Format: Plain text (`.txt`)

### 5️⃣ Run the Pipeline

```bash
python main.py --topic "Your Podcast Topic"
```

---

## 🔄 Input Detection Logic

The system uses a **priority cascade** for input detection:

| Priority | Behavior | Command Example |
|----------|----------|-----------------|
| **1** | User provides `--audio` → Always used | `python main.py --topic "AI" --audio "episode.mp3"` |
| **2** | No `--audio` → Auto-detects first audio in `podcast_recordings/` | `python main.py --topic "AI"` |
| **3** | User provides `--transcript` → Used if no audio | `python main.py --topic "AI" --transcript "transcript.txt"` |
| **4** | No inputs → Auto-detects first transcript in `test_data/` | `python main.py --topic "AI"` |
| **5** | Nothing found → Exits with error | NA |

> **Note:** Files are detected in **alphabetical order** for deterministic behavior.

---

## 📊 Pipeline Workflow

### Stage 1: Ingest (Sequential)
```
Audio File → Google GenAI → Transcript Text
     OR
Transcript File → Load Directly
```

### Stage 2: Research (Sequential)
```
Topic + Transcript Sample → Research Agent → Background Info
```

### Stage 3: Outline (Sequential)
```
Research + Transcript → Outline Agent → Episode Structure
```

### Stage 4: Assets (Parallel) ⚡
```
                    ┌─→ Show Notes Agent  → show_notes.json
                    ├─→ Timestamp Agent   → timestamps.json
Transcript + Outline┼─→ Quote Agent       → quotes.json
                    ├─→ Social Agent      → social.json
                    └─→ SEO Agent         → seo.json
```

---

## 🖥️ Dashboard

### Launching the Dashboard

After pipeline completion, you'll be prompted:

```
Do you want to launch the dashboard now? (y/n): y

🌐 Launching Dashboard at http://127.0.0.1:5000 ...
✓ Dashboard server started successfully!
Visit http://127.0.0.1:5000 to view your podcast assets

📌 Dashboard is running at http://127.0.0.1:5000
Press Ctrl+C to stop the dashboard and exit
```
### Stopping the Dashboard

Simply press **Ctrl+C** in the terminal where you launched `main.py`:

```
^C
⚠️  Stopping dashboard...
✓ Dashboard stopped. Goodbye!
```

### Manual Dashboard Launch

If you skipped the prompt, you can launch it manually:

```bash
cd dashboard
python dashboard_server.py
```

Then visit: http://127.0.0.1:5000

---

## 🛠️ Tools & Utilities

### Audio Tool (`audio_tool.py`)
This tool uploads audio to Google GenAI File API, polls until file processing completes, extracts and returns structured transcript and also handles large audio files (up to 2GB).

### Search Tool (`search_tool.py`)
This tool provides web search via DuckDuckGo HTML, extracts titles, URLs, snippets, powers the research agent.

### Custom Tools (`custom_tools.py`)
This tool includes two utility methods: `save_to_file()` for clean JSON output writer and `read_transcript()` to transcript file loader. This centralizes file I/O logic

### ADK Tool Wrappers (`adk_tool_wrappers.py`)
This tool standardizes `success()` and `failure()` responses, ensures consistent tool output format and simplifies error handling across agents

### Schemas (`schemas.py`)
This is validation tool which incorporates pydantic models for all agent outputs, do runtime validation of JSON structures and ensures data integrity across pipeline. 

---

## 🧪 Testing

### Test Scenarios

#### 1. With Audio File
```bash
python main.py --topic "AI Agents" --audio "podcast_recordings/test_episode.mp3"
```
**Expected:** Transcription → Full pipeline → 8 JSON outputs

#### 2. With Transcript File
```bash
python main.py --topic "AI Agents" --transcript "test_data/sample_transcript.txt"
```
**Expected:** Skip transcription → Full pipeline → 8 JSON outputs

#### 3. Auto-Detection
```bash
python main.py --topic "AI Agents"
```
**Expected:** Detects first audio/transcript → Full pipeline → 8 JSON outputs

#### 4. No Inputs
```bash
python main.py --topic "AI Agents"
# With empty podcast_recordings/ and test_data/
```
---

## 🔍 Troubleshooting Common Issues

#### ❌ "Transcription failed: unknown"

**Cause:** Audio file processing error

**Solution:**

1. Ensure Google GenAI API is enabled
2. Verify audio file format (`.mp3`, `.wav`, `.m4a`)
3. Check file size (< 2GB)

#### ❌ "Rate limit exceeded"

**Cause:** Too many API requests

**Solution:**
- Wait 5-15 seconds
- Check your API quota

---

## ⚖️ License

This project is licensed under the Apache License 2.0 - see below for details:

```
Copyright 2025 Revanth Sai R

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

🎥 Video Pipeline (Future Work)

```
Video File (MP4 / MOV)
        ↓
Video Processing Layer
    ├─→ Extract Audio → Transcription
    ├─→ Generate Video Clips (viral moments)
    └─→ Create Thumbnails
        ↓
Research & Outline (same as current pipeline)
        ↓
Content Generation (enhanced with video context)
    ├─→ Video with timestamps and notes
    ├─→ Social Clips from actual video
    ├─→ Thumbnail Creaton
        ↓
Output: Complete Video + Audio + Text Bundle

```
---
**Made with ❤️ by [Revanth Sai R](https://github.com/revanthrsai)**
