# Server Management Guide

## Starting the Local Server

### Quick Start

```bash
cd nyc-american-chestnut-map-2025
python3 -m http.server 8000
```

The map will be available at: **http://localhost:8000**

### Background Server (Recommended)

Run the server in the background so you can continue using the terminal:

```bash
python3 -m http.server 8000 > /dev/null 2>&1 &
```

This will:
- Start server on port 8000
- Suppress output (`> /dev/null 2>&1`)
- Run in background (`&`)

## Stopping the Server

### Method 1: Find and Kill Process (Safest)

```bash
# Find the server process
ps aux | grep "http.server" | grep -v grep

# You'll see output like:
# jose_d_sandoval  27224   0.0  0.0 ... python3 -m http.server 8000

# Kill the process using the PID (first number after username)
kill 27224
```

### Method 2: Kill by Port

```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill $(lsof -ti:8000)
```

### Method 3: Kill All Python HTTP Servers

```bash
# WARNING: This kills ALL python http.server processes
pkill -f "python.*http.server"
```

### Method 4: If Server is in Foreground

If you started the server without `&` (background):
- Press `Ctrl+C` in the terminal to stop it

## Restarting the Server

After updating `data/trees.json` or modifying `index.html`:

```bash
# Stop the server
kill $(lsof -ti:8000)

# Start it again
python3 -m http.server 8000 > /dev/null 2>&1 &
```

**Important**: Your browser may cache the old JSON file. After restarting:
1. Open http://localhost:8000
2. **Hard refresh**:
   - Mac: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + Shift + R`
   - Or clear browser cache

## Checking Server Status

### Is the server running?

```bash
lsof -i:8000
```

**Output if running**:
```
COMMAND   PID  USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
Python  27224  jose    3u  IPv4 ...      0t0  TCP *:8000 (LISTEN)
```

**Output if not running**:
```
(no output)
```

### Quick status check

```bash
curl -I http://localhost:8000 2>/dev/null | head -1
```

**If running**: `HTTP/1.0 200 OK`
**If not running**: (no output or connection error)

## Port Already in Use?

If you see: `OSError: [Errno 48] Address already in use`

```bash
# Find what's using port 8000
lsof -i:8000

# Kill it
kill $(lsof -ti:8000)

# Or use a different port
python3 -m http.server 8001
```

## Server Logs

### View Real-Time Logs

If server is running in foreground, logs appear automatically.

If running in background, view logs:

```bash
# Start with logging to file
python3 -m http.server 8000 > server.log 2>&1 &

# Watch logs in real-time
tail -f server.log
```

### Example Log Output

```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
127.0.0.1 - - [06/Dec/2025 08:15:23] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [06/Dec/2025 08:15:23] "GET /data/trees.json HTTP/1.1" 200 -
```

## Accessing from Other Devices

### On Same Network (Phone/Tablet)

1. Find your computer's IP address:
   ```bash
   # Mac/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1

   # Windows
   ipconfig
   ```

2. Start server on all interfaces:
   ```bash
   python3 -m http.server 8000 --bind 0.0.0.0
   ```

3. On other device, visit:
   ```
   http://YOUR_IP_ADDRESS:8000
   ```

   Example: `http://192.168.1.100:8000`

## Common Issues

### 1. Changes Not Showing

**Problem**: Updated `trees.json` but map shows old data

**Solutions**:
- Hard refresh browser (`Cmd+Shift+R` or `Ctrl+Shift+R`)
- Clear browser cache
- Check file modification time:
  ```bash
  ls -lh data/trees.json
  stat -f "%Sm" data/trees.json  # Mac
  stat -c "%y" data/trees.json   # Linux
  ```

### 2. Server Won't Start

**Problem**: `Address already in use`

**Solution**:
```bash
kill $(lsof -ti:8000)
python3 -m http.server 8000
```

### 3. Can't Access from Phone

**Problem**: Map works on computer but not phone on same network

**Solutions**:
- Ensure server bound to `0.0.0.0`:
  ```bash
  python3 -m http.server 8000 --bind 0.0.0.0
  ```
- Check firewall settings
- Verify both devices on same WiFi network

### 4. Permission Denied

**Problem**: `Permission denied` on port 80 or 443

**Solution**: Use port >= 1024 (like 8000) which doesn't require admin

## Production Deployment

For deploying to the web (GitHub Pages), you don't need to run a local server.

See [README.md](README.md) for GitHub Pages deployment instructions.

## Quick Reference

| Task | Command |
|------|---------|
| Start server | `python3 -m http.server 8000` |
| Start in background | `python3 -m http.server 8000 > /dev/null 2>&1 &` |
| Stop server | `kill $(lsof -ti:8000)` |
| Check if running | `lsof -i:8000` |
| Restart server | `kill $(lsof -ti:8000) && python3 -m http.server 8000 &` |
| View in browser | Open `http://localhost:8000` |
| Hard refresh | Mac: `Cmd+Shift+R`, Windows: `Ctrl+Shift+R` |

## Aliases (Optional)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Chestnut map aliases
alias map-start='cd ~/path/to/nyc-american-chestnut-map-2025 && python3 -m http.server 8000 > /dev/null 2>&1 &'
alias map-stop='kill $(lsof -ti:8000)'
alias map-restart='kill $(lsof -ti:8000); python3 -m http.server 8000 > /dev/null 2>&1 &'
alias map-open='open http://localhost:8000'
```

Then use:
```bash
map-start    # Start server
map-open     # Open in browser
map-restart  # Restart after changes
map-stop     # Stop server
```

## Security Notes

- **Local development only**: This server is for local testing, not production
- **No HTTPS**: Data transmitted unencrypted
- **No authentication**: Anyone on network can access
- **For production**: Use GitHub Pages or proper web server

## After Rebuilding Data

Whenever you run:
- `python3 build_trees_with_accuracy.py`
- `python3 build_with_landuse_validation.py`
- `python3 update_confirmed_coordinates.py`

You **must**:
1. **Hard refresh** the browser (`Cmd+Shift+R`)
2. Or **restart the server**:
   ```bash
   kill $(lsof -ti:8000)
   python3 -m http.server 8000 > /dev/null 2>&1 &
   ```

The browser caches `data/trees.json` aggressively, so a normal refresh won't load new data.

---

**Current Server Status**: Running at http://localhost:8000
**To Stop**: `kill $(lsof -ti:8000)`
**To Restart**: Run the commands above
