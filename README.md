# AI Lecture Question Generation System

## Overview

This project is an AI-powered FastAPI backend that automatically processes course videos and generates summaries and multiple-choice questions. The system is designed to handle long lecture videos efficiently using chunk-based processing, multi-model AI orchestration, and batch-based execution. It converts lecture videos into structured learning material by generating concise summaries, detailed summaries, and categorized questions.

---

## Features

- AI-based Lecture Summary Generation
- Automatic Multiple-Choice Question Generation
- Chunk-Based Video Processing
- Multi-Model Question Generation
- Best Question Selection Model
- Batch Processing for Scalability
- Dynamic Video Regeneration Logic
- Cumulative Context-Based Learning
- MongoDB Storage
- Async Processing for Performance Optimization

---

## System Architecture

The system follows a multi-stage AI processing pipeline:

---

## How It Works

### Step 1: Video Processing

- Download course video from URL
- Convert video to audio
- Transcribe audio to text
- Convert text into PDF

### Step 2: Chunk-Based Processing

- Split PDF into smaller pages
- Process each page individually
- Generate concise and detailed summaries
- Maintain cumulative summary context

### Step 3: Question Generation

- Generate questions using multiple AI models in parallel
- Apply difficulty categorization (Easy, Medium, Hard)
- Use selection model to pick best questions

### Step 4: Cumulative Learning

- Combine summaries across lectures
- Generate progressive questions
- Maintain lecture-level understanding

### Step 5: Data Storage

- Store summaries and questions in MongoDB
- Track processed videos
- Enable dynamic regeneration

---

## Batch Processing

To handle large courses efficiently, videos are processed in batches:

- Videos split into batches of 5
- Each batch processed sequentially
- Memory cleanup after each batch
- Prevents memory overflow

---

## Dynamic Regeneration Logic

The system intelligently detects new videos and processes only required ones:

### Supported Scenarios

- New Course Processing
- Videos Added at Beginning
- Videos Added in Middle
- Videos Added at End
- Mixed Updates

This avoids reprocessing all videos and improves performance.

---

## Tech Stack

### Backend
- FastAPI
- Python
- AsyncIO

### AI & LLM
- LangChain
- Prompt Engineering
- Multi-Model Orchestration

### Database
- MongoDB

### Processing
- Video Processing
- Speech-to-Text
- PDF Processing

---

## API Endpoint

### Generate Questions

### Request Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| course_id | string | Course ID |
| number_of_questions | integer | Number of questions |
| hinglish | boolean | Hinglish transcription |

---

## Example Request

```json
{
  "course_id": "123",
  "number_of_questions": 9,
  "hinglish": false
}
```

## Challenges Solved

### Chunk-Based Processing
Handling long lecture videos by splitting them into smaller page-level chunks and maintaining cumulative context across pages for accurate summarization and question generation.

### Multi-Model Question Generation
Generating questions using multiple AI models in parallel and selecting the best ones using a selection model to improve quality and reduce hallucinations.

### Batch Processing
Processing videos in batches to efficiently manage memory usage and prevent system overload while handling large course datasets.

### Dynamic Regeneration
Implementing smart logic to process only newly added or modified videos instead of reprocessing the entire course, improving performance and scalability.

---

## Performance Optimizations

### Async Processing
Used asynchronous operations to handle video processing, transcription, and AI model execution efficiently.

### Batch Execution
Implemented batch-based processing to manage large datasets and improve system scalability.

### Memory Cleanup
Added cleanup mechanisms after each batch to free system memory and avoid performance degradation.

### Parallel Model Execution
Executed multiple AI models in parallel for faster and higher-quality question generation.
