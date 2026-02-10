# Shein Creator Token Generator

Automated Shein creator token generation script with web dashboard for monitoring.

## Features

- 🔄 **Continuous Loop Mode** - Runs indefinitely in batches
- 🌐 **Web Dashboard** - Live terminal output, statistics, and coupons display
- 📊 **Real-time Stats** - Track batch progress and cumulative results
- 🎟️ **Coupon Extraction** - Automatically extracts and saves coupons
- 📱 **Mobile Responsive** - Dashboard works on desktop and mobile
- ☁️ **Railway Ready** - Pre-configured for Railway.app deployment

## Local Usage

### Installation

```bash
pip install -r requirements.txt
```

### Run Script

```bash
# Default: 5 accounts per batch, continuous loop
python shein_creator_token_nologin.py

# Custom target
python shein_creator_token_nologin.py --target=10000

# Custom concurrency
python shein_creator_token_nologin.py --target=5000 --concurrency=200
```

### Access Dashboard

- Automatically opens at `http://127.0.0.1:5000`
- View live terminal output
- Monitor statistics (batch, accounts, coupons)
- Download extracted coupons

### Stop Script

Press `Ctrl+C` to stop gracefully with summary.

## Railway.app Deployment

### Prerequisites

1. [Railway.app account](https://railway.app/)
2. GitHub repository with this code

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [Railway.app](https://railway.app/)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Python and deploy

3. **Access Dashboard**
   - Railway will assign a public URL
   - Click "Generate Domain" in Railway dashboard
   - Access your dashboard at `https://<your-app>.up.railway.app`

4. **Monitor Logs**
   - View deployment logs in Railway dashboard
   - Check "Deployments" tab for status

### Configuration Files

- **`railway.json`** - Deployment configuration
- **`requirements.txt`** - Python dependencies
- **`runtime.txt`** - Python version (3.11)
- **`.railwayignore`** - Files to exclude from deployment

### Environment Variables (Optional)

Set in Railway dashboard if needed:
- `TARGET` - Default target accounts per batch (default: 5)
- `PORT` - Web dashboard port (Railway auto-assigns)

## Files Generated

- **`shein2.json`** - Raw API responses with tokens
- **`extracted_coupons.txt`** - Extracted coupon codes
- **`used_num.txt`** - Phone numbers already used (prevents duplicates)

## Command-Line Options

```
--target=N              Number of accounts per batch (default: 5)
--concurrency=N         Concurrent requests (default: 500)
--delay=N               Delay between requests in ms (default: 50)
--country=CODE          Country code (default: +91)
--prefix=N              Phone number prefix
--digits=N              Phone number digits (default: 10)
--phone=NUMBER          Test specific phone number
--coupon-concurrency=N  Concurrent coupon fetches (default: 500)
--coupon-output=FILE    Coupon output file (default: extracted_coupons.txt)
--output=FILE           Token output file (default: shein2.json)
--input-json=FILE       Load phones from JSON file
--update-json=FILE      Update JSON file with new tokens
--force                 Ignore existing phone numbers
--help                  Show help message
```

## Technical Stack

- **Python 3.11**
- **Flask** - Web server for dashboard
- **Requests** - HTTP client for API calls
- **Server-Sent Events (SSE)** - Live log streaming
- **Concurrent Futures** - Parallel token generation

## Dashboard Features

### Live Terminal
- Real-time script output streaming
- Auto-scrolling terminal view
- Syntax highlighting

### Statistics Panel
- Current batch number
- Total accounts checked
- Total coupons found
- Current batch progress

### Coupons Table
- Phone number
- Coupon code
- Value
- Minimum order
- One-click download

## Notes

- Script runs continuously until manually stopped (Ctrl+C)
- Each batch generates new random phone numbers
- Coupons are automatically extracted from successful tokens
- Dashboard updates in real-time (no refresh needed)
- Mobile-responsive design for monitoring on the go

## Troubleshooting

### Dashboard not opening
- Check if Flask is installed: `pip install flask`
- Verify port 5000 is not in use
- Check firewall settings

### Railway deployment fails
- Verify `requirements.txt` is present
- Check Railway build logs for errors
- Ensure Python 3.11 is specified in `runtime.txt`

### No coupons found
- This is normal - not all accounts have coupons
- Script continues running to find more
- Check `extracted_coupons.txt` for any found coupons

## License

MIT License - Free to use and modify
