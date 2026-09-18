## Setup

### 1. Clone the repository

```bash
git clone git@github-msashahid:msaShahid/GenAIApplication.git
cd GenAIApplication
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Linux / macOS (bash/zsh):**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

> ⚠️ If PowerShell blocks the activation script, run this once in an **admin** PowerShell:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

### 4. Upgrade pip (recommended)

```bash
python -m pip install --upgrade pip
```

### 5. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables (if applicable)

Create a `.env` file in the project root:

```env
# Example — replace with your actual keys
OPENAI_API_KEY=your_api_key_here
```

### 7. Verify the setup

```bash
python -c "import sys; print(sys.executable)"
```

You should see a path pointing to `.venv`, confirming the virtual environment is active.
