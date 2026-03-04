# Troubleshooting

Common issues and solutions when using TubeFetch.

---

## "This video is not available" Errors

### Symptom

You see errors like:

```
ERROR: [youtube] VIDEO_ID: This video is not available
ERROR    Metadata error for VIDEO_ID: Failed to extract metadata
```

But the video plays fine in your browser.

### Cause

This happens when **yt-dlp** (the default metadata backend) is blocked from accessing the video. Common reasons:

1. **Age-restricted content** - Video requires sign-in to verify age
2. **Geographic restrictions** - Content blocked in your region via yt-dlp
3. **YouTube bot detection** - yt-dlp being blocked by anti-bot measures
4. **Membership-only content** - Video requires channel membership

### Solution: Use YouTube Data API v3

The YouTube Data API v3 backend can access metadata for restricted videos without triggering bot detection.

#### Step 1: Install the optional dependency

```bash
pip install tubefetch[youtube-api]
```

#### Step 2: Get a YouTube Data API key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **YouTube Data API v3**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key

#### Step 3: (Optional) Restrict your API key

For security, restrict your API key:

1. Click on your API key in the credentials list
2. Under "API restrictions":
   - Select "Restrict key"
   - Check only "YouTube Data API v3"
3. Under "Application restrictions":
   - Select "IP addresses"
   - Add your IP address (find it with `curl ifconfig.me`)
   - Or select "None" for testing (less secure)
4. Click "Save"

#### Step 4: Set your API key

```bash
export TUBEFETCH_YT_API_KEY="your-api-key-here"
```

Or add to `tubefetch.yaml`:

```yaml
yt_api_key: your-api-key-here
```

#### Step 5: Retry your command

```bash
tubefetch VIDEO_ID --download video
```

TubeFetch will automatically use the YouTube Data API for metadata when the key is set, and fall back to yt-dlp if the API fails.

### Important Notes

**Quota Limits:**
- YouTube Data API has a default quota of **10,000 units per day**
- Each video metadata request costs **1 unit**
- You can fetch ~10,000 videos per day with the API
- Check your quota usage in [Google Cloud Console](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)

**What Works Without API Key:**
- ✅ **Transcripts** - Always work (uses `youtube-transcript-api`)
- ❌ **Metadata** - May fail for restricted videos (uses yt-dlp by default)
- ❌ **Media downloads** - May fail for restricted videos (uses yt-dlp)

**Limitations:**
- YouTube Data API can fetch metadata but **cannot download media** for restricted videos
- For age-restricted video downloads, you need to use yt-dlp with cookies (see below)

---

## Downloading Age-Restricted Videos

If you need to download media from age-restricted videos, you need to authenticate yt-dlp with browser cookies.

### Step 1: Export cookies from your browser

1. Install a browser extension:
   - Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Go to YouTube and sign in
3. Click the extension icon and export cookies to `cookies.txt`

### Step 2: Pass cookies to yt-dlp

Currently, TubeFetch doesn't have built-in cookie file support. This is a planned feature.

**Workaround:** Use yt-dlp directly for media, then use TubeFetch for metadata/transcripts:

```bash
# Fetch metadata and transcripts with TubeFetch
tubefetch VIDEO_ID

# Download media with yt-dlp using cookies
yt-dlp --cookies cookies.txt -o "out/VIDEO_ID/media/%(title)s.%(ext)s" VIDEO_ID
```

---

## Rate Limiting

If you're fetching many videos and hitting rate limits:

### Adjust rate limit settings

```bash
tubefetch --rate-limit 1.0 --file videos.txt
```

Or in `tubefetch.yaml`:

```yaml
rate_limit: 1.0  # requests per second
```

### Use YouTube Data API

The YouTube Data API has higher rate limits than yt-dlp scraping:

```bash
export TUBEFETCH_YT_API_KEY="your-key"
tubefetch --file videos.txt
```

---

## Transcript Not Available

### Symptom

```
ERROR    Transcript error for VIDEO_ID: No transcript found
```

### Causes

1. **No captions available** - Video has no subtitles/captions
2. **Language mismatch** - Requested language not available
3. **Live stream** - Live streams don't have transcripts until archived

### Solutions

**Allow auto-generated transcripts:**

```bash
tubefetch VIDEO_ID --allow-generated
```

**Allow any language as fallback:**

```bash
tubefetch VIDEO_ID --allow-any-language
```

**Specify multiple language preferences:**

```bash
tubefetch VIDEO_ID --languages "en,es,fr"
```

---

## Connection Errors

### Symptom

```
ERROR    Network error: Connection timeout
```

### Solutions

**Increase retry count:**

```bash
tubefetch VIDEO_ID --retries 5
```

**Check your internet connection:**

```bash
curl -I https://www.youtube.com
```

**Use a VPN** if YouTube is blocked in your region.

---

## Getting Help

If you're still having issues:

1. **Check the logs** - Look in `out/VIDEO_ID/` for detailed error messages
2. **Update dependencies**:
   ```bash
   pip install --upgrade tubefetch yt-dlp
   ```
3. **File an issue** - [GitHub Issues](https://github.com/pointmatic/tubefetch/issues)
   - Include the full error message
   - Include the video ID (if not private)
   - Include your TubeFetch version: `tubefetch --version`
