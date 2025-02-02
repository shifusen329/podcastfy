# Podcastfy Development Tasks

## 1. Image Processing Support
- [x] Test image content extraction functionality
- [x] Verify LLM handling of image descriptions
- [x] Test transcript generation from image content
- [x] Test TTS generation with image-based transcripts
- [x] Add error handling for image processing failures
- [ ] Add base64 encoding for local image files
- [ ] Support Google Cloud Storage URIs for images
- [ ] Add image format validation
- [ ] Implement image size optimization

## 2. Add Voice Selection for Cloud TTS Providers
- [ ] Add OpenAI voice options:
  - alloy
  - echo
  - fable
  - onyx
  - nova
  - shimmer
- [ ] Add Gemini voice options:
  - Journey-D
  - Journey-O
  - Other available voices
- [ ] Update voice.py handler to show voice dropdowns for cloud providers
- [ ] Update voice component UI to display available voices
- [ ] Add voice preview descriptions

## 3. Add Voice Sampling for Cloud TTS Providers
- [ ] Create sample text generator for each provider
- [ ] Implement sample audio generation
- [ ] Add sample button to UI for cloud providers
- [ ] Cache sample audio to avoid regeneration
- [ ] Add loading states during sample generation

## 4. Fine-tune Longform Chunking
- [ ] Analyze current chunking algorithm
- [ ] Test different chunk sizes and counts
- [ ] Measure output length vs settings
- [ ] Update UI descriptions to match actual output
- [ ] Add more granular chunk settings:
  - Minimum chunk size
  - Maximum chunk size
  - Overlap settings
  - Context window settings

## 5. Add LLM Selection for Transcript Generation
- [ ] Add LLM model dropdown to UI
- [ ] Support OpenAI models:
  - GPT-4
  - GPT-3.5
- [ ] Support Anthropic models:
  - Claude
- [ ] Support Google models:
  - Gemini
- [ ] Add model-specific settings:
  - Temperature
  - Top-p
  - Max tokens
  - Other relevant parameters

## 6. Add Local Ollama Integration
- [ ] Add Ollama endpoint configuration
- [ ] Support model listing from Ollama
- [ ] Add model selection UI
- [ ] Handle Ollama-specific parameters:
  - Context window
  - Temperature
  - Top-k
  - Top-p
- [ ] Add error handling for endpoint connectivity

## 7. Add Sequential Workflow Option
- [ ] Add workflow selection UI:
  - One-shot (current)
  - Sequential (new)
- [ ] Split transcript/TTS into separate steps
- [ ] Add transcript preview/edit step
- [ ] Add progress tracking for each step
- [ ] Allow saving intermediate results
- [ ] Add ability to resume from saved state

## 8. Add Wordcount Target Feature
- [ ] Add wordcount input field
- [ ] Update chunking algorithm to target wordcount
- [ ] Add wordcount estimation
- [ ] Add progress towards target display
- [ ] Add validation for min/max wordcount limits

## Notes
- Each task should include appropriate error handling
- Add logging for debugging
- Update documentation for new features
- Add tests for new functionality
- Consider performance implications
