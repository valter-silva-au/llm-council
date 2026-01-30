# Debugging Guide for LLM Council

## Chairman Synthesis Failures ("Unable to generate final synthesis")

### Quick Diagnosis

Run the test scripts to identify the issue:

```bash
# Test if Chairman model works at all
python test_chairman.py

# Test Chairman with realistic Stage 3 context
python test_stage3.py

# Test web search providers
python test_search.py
```

### Common Causes

#### 1. **Timeout Issues** (Most Common)
**Symptom:** Chairman returns None after ~2 minutes

**Cause:** Stage 3 prompts are very large (all Stage 1 responses + Stage 2 rankings). The Chairman needs time to process this context.

**Fix Applied:**
- Increased Chairman timeout from 120s → 180s (3 minutes)
- Added prompt size logging to track context length
- Location: `backend/council.py:255-258`

**Check Logs For:**
```
Stage 3: Chairman prompt is XXX characters (~YYY tokens)
Stage 3: Using timeout of 180.0s for Chairman synthesis
```

#### 2. **AWS Configuration Issues**
**Symptoms:**
- "Unable to locate credentials"
- "Access Denied"
- "Region not supported"

**Fix:**
- Verify AWS credentials: `~/.aws/credentials`
- Check region: `.env.dev` should have `AWS_REGION=us-west-2`
- Verify Bedrock model access in your AWS account

**Test:**
```bash
aws bedrock-runtime invoke-model \
  --model-id us.amazon.nova-premier-v1:0 \
  --region us-west-2 \
  --body '{"messages":[{"role":"user","content":[{"text":"Hello"}]}]}' \
  --cli-binary-format raw-in-base64-out \
  output.json
```

#### 3. **Model Quota/Throttling**
**Symptoms:**
- "ThrottlingException"
- "Rate exceeded"
- Works sometimes, fails other times

**Check:**
- AWS Service Quotas console
- CloudWatch metrics for throttling
- Request frequency during council runs

**Fix:**
- Reduce council size (fewer models)
- Add retry logic with exponential backoff
- Request quota increase from AWS

#### 4. **Context Window Exceeded**
**Symptoms:**
- "ValidationException"
- "Input too long"

**Note:** Nova Premier has 300K token input limit, so this is unlikely unless:
- Using many council models (>6)
- Very long user queries
- Extensive conversation history

**Fix:**
- Truncate Stage 1/Stage 2 responses before Stage 3
- Summarize rankings instead of including full text
- Use a smaller council

#### 5. **Model Not Available**
**Symptoms:**
- "ResourceNotFoundException"
- "Model not found"

**Fix:**
- Check model ID is correct: `us.amazon.nova-premier-v1:0`
- Verify model is available in your region
- Try alternative: `us.amazon.nova-lite-v1:0`

### Improvements Made

#### Enhanced Logging
**Files Modified:** `backend/council.py`, `backend/bedrock.py`

**New Logs:**
- Prompt size tracking (characters + estimated tokens)
- Timeout values for each stage
- Detailed Bedrock error codes and messages
- Response size tracking

**Example:**
```
[INFO] Stage 3: Chairman prompt is 12,345 characters (~3,086 tokens)
[DEBUG] Model us.amazon.nova-premier-v1:0: Prompt size ~12345 chars (~3086 tokens)
[ERROR] Error code: ThrottlingException
[ERROR] Error message: Rate exceeded for model invocations
```

#### Increased Timeouts
- **Chairman timeout:** 120s → 180s (Stage 3 needs more time)
- **Configurable:** Easy to adjust in `council.py`

#### Better Error Handling
- Catch and log exceptions during Chairman query
- Detailed error messages with troubleshooting hints
- Graceful degradation (error message instead of crash)

#### Max Tokens Configuration
- Claude models: 16,000 tokens (extended thinking)
- Nova models: 8,000 tokens (standard)
- Location: `backend/bedrock.py:95-100`

### Monitoring During Council Runs

**Enable DEBUG logging in `.env.dev`:**
```bash
DEBUG=true
```

**Check logs for:**
1. Stage 1: How many models responded?
   ```
   Stage 1 complete: 4/4 models responded
   ```

2. Stage 2: Were rankings collected?
   ```
   Stage 2 complete: 4/4 rankings collected
   ```

3. Stage 3: Prompt size and timing
   ```
   Stage 3: Chairman prompt is XXX characters
   Stage 3: Chairman synthesized YYY chars
   ```

4. Bedrock API errors:
   ```
   Error querying Bedrock model: ...
   Error code: ...
   Error message: ...
   ```

### Performance Tuning

#### For Faster Results
1. **Reduce council size** - Use 2-3 models instead of 4
2. **Use faster models** - Nova Lite instead of Nova Premier
3. **Disable extended thinking** - For Claude models
4. **Shorter prompts** - Summarize Stage 1 responses

#### For Better Quality
1. **Longer timeouts** - 240s+ for complex queries
2. **More models** - Diverse perspectives
3. **Extended thinking** - For Claude models
4. **Larger context** - Include full Stage 1/Stage 2 content

### When to Switch Chairman Models

**Current:** `us.amazon.nova-premier-v1:0` (heavyweight synthesis)

**Alternatives:**

| Model | Speed | Quality | Cost | When to Use |
|-------|-------|---------|------|-------------|
| Nova Lite | Fast | Good | Low | Quick answers, simple queries |
| Nova Pro | Medium | Better | Medium | Balanced performance |
| Claude Sonnet 4.5 | Slow | Best | High | Maximum quality needed |
| Claude Opus 4.5 | Slowest | Best | Highest | Complex reasoning |

**To change:** Edit `BEDROCK_CHAIRMAN_MODEL` in `backend/config.py`

### Testing Changes

After making configuration changes:

```bash
# 1. Test basic connectivity
python test_chairman.py

# 2. Test realistic Stage 3 scenario
python test_stage3.py

# 3. Run a full council query via the UI
# Check browser console and backend logs
```

### Getting Help

If issues persist:

1. **Collect logs:**
   ```bash
   # Backend logs
   cat scripts/.backend.log

   # Run with DEBUG=true
   DEBUG=true uv run python -m backend.main
   ```

2. **Run diagnostics:**
   ```bash
   python test_chairman.py > chairman_test.log 2>&1
   python test_stage3.py > stage3_test.log 2>&1
   ```

3. **Check AWS CloudWatch:**
   - Service: Bedrock
   - Metric: Invocations, ThrottleCount, ModelInvocationLatency
   - Filter by model ID

4. **Verify model access:**
   - AWS Console → Bedrock → Model access
   - Ensure Nova Premier is "Access granted"
   - Check region matches .env.dev
