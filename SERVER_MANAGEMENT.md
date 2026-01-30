# 🍽️ Platter Compiler Webapp - Server Management

This project uses a modern Node.js-based server management system that handles both the Python backend and Svelte frontend in a single terminal process.

## 🎨 Architecture Overview

- **Single Script**: `server-manager.js` - Comprehensive Node.js server manager
- **Virtual Environment**: Automatic Python venv creation and management
- **Unified Terminal**: Everything runs in one terminal, no multiple windows
- **Smart Dependencies**: Auto-installs requirements.txt packages
- **Graceful Shutdown**: Ctrl+C stops everything cleanly

## 📁 Available Commands

### Core Commands
```bash
# Start both servers (default)
node server-manager.js start
node server-manager.js        # same as start

# Stop all servers
node server-manager.js stop

# Restart all servers
node server-manager.js restart

# Setup/check virtual environment only
node server-manager.js venv
```

### NPM Scripts (from frontend directory)
```bash
npm run start:dev     # Start both servers
npm run stop:dev      # Stop all servers
npm run restart:dev   # Restart all servers
npm run setup:venv    # Setup virtual environment
```

### Batch Files (for double-clicking)
- **`start-servers.bat`** - Invokes Node.js manager to start
- **`stop-servers.bat`** - Invokes Node.js manager to stop

## 🚀 How to Use

### Starting Development

**Option 1: Terminal (Recommended)**
```bash
# From project root
node server-manager.js start
```

**Option 2: NPM Script**
```bash
# From frontend directory
npm run start:dev
```

**Option 3: Double-Click**
- Double-click `start-servers.bat`

### Stopping Development

**Option 1: Keyboard Shortcut**
- Press `Ctrl+C` in the running terminal

**Option 2: Separate Command**
```bash
node server-manager.js stop
```

**Option 3: Double-Click**
- Double-click `stop-servers.bat`

## ✨ Features

### 🐍 Python Virtual Environment
- **Auto-Creation**: Creates `.venv` in backend directory if missing
- **Smart Checking**: Verifies venv completeness and required packages
- **Auto-Install**: Installs `requirements.txt` packages automatically
- **Isolation**: Uses venv Python instead of global installation

### 📋 Process Management
- **Port Checking**: Detects and handles port conflicts (8000, 5173)
- **Clean Shutdown**: Properly terminates all spawned processes
- **Error Handling**: Graceful error messages and recovery
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 🎨 User Experience
- **Single Terminal**: No multiple windows or complex setup
- **Colored Output**: Easy-to-read status messages with emojis
- **Interactive Prompts**: Asks before stopping conflicting processes
- **URL Display**: Shows exact URLs when servers are ready

## 🔧 Requirements

### Prerequisites
- **Node.js** (for the server manager)
- **Python 3.7+** (for backend)
- **npm** (for frontend dependencies)

### First Time Setup
**Automatic (Recommended):**
```bash
# Just run the server manager - it handles everything!
node server-manager.js start
```

**Manual (if needed):**
```bash
# Install frontend dependencies
cd frontend && npm install

# The Python venv and backend deps are handled automatically
```

## 📍 URLs

After starting:
- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (FastAPI auto-docs)

## 💡 Tips

1. **Virtual Environment Location**: Created at `backend/.venv/`
2. **Requirements**: Automatically reads `backend/requirements.txt`
3. **Port Conflicts**: Manager will ask before killing conflicting processes
4. **Development Flow**: Start once, code all day, Ctrl+C to stop
5. **Logs**: All output appears in the same terminal for easy debugging

## 🔄 Migration from Old Scripts

If you were using the old PowerShell scripts:
- **Old**: `start-servers.ps1` → **New**: `node server-manager.js start`
- **Old**: `stop-servers.ps1` → **New**: `Ctrl+C` or `node server-manager.js stop`
- **Benefits**: Single terminal, auto venv, better error handling

## 🎉 One-Terminal Development

With the new system:
1. **Start**: `node server-manager.js start`
2. **Code**: Everything runs in one terminal with colored output
3. **Stop**: Press `Ctrl+C` to stop everything cleanly
4. **Develop**: Open http://localhost:5173 and start coding!


