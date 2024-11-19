# Installing KitchenAI 🛠️

### 💡 **Pro Tip**: Always start with a virtual environment!  
Creating a virtual environment isolates your dependencies, ensuring a smooth setup for KitchenAI.

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

---

## 📦 Installing via PyPI
You can install KitchenAI directly from [PyPI](https://pypi.org/project/kitchenai/):

```bash
pip install kitchenai
```

---

## ✅ Verifying Your Installation

To confirm KitchenAI is installed and working correctly, use the following command:

```bash
kitchenai --help
```

### Example Output:
```plaintext
 Usage: kitchenai [OPTIONS] COMMAND [ARGS]...
 
╭─ Options ─────────────────────────────────────────────────────────────────────────────╮
│ --install-completion  Install completion for the current shell.                      │
│ --show-completion     Show completion for the current shell, to copy or customize.   │
│ --help                Show this message and exit.                                    │
╰───────────────────────────────────────────────────────────────────────────────────────╯

╭─ Commands ────────────────────────────────────────────────────────────────────────────╮
│ add                                                                                │
│ init                                                                               │
│ qcluster   Run Django-q cluster.                                                  │
│ runserver  Run Django runserver.                                                  │
│ dev        Start the KitchenAI server in development mode.                        │
│ manage     Run Django's manage.py commands.                                       │
│ build      Build your KitchenAI application.                                      │
│ new        Create a new KitchenAI project.                                        │
│ cook       Run predefined KitchenAI workflows.                                    │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

---

## 🔧 Initializing KitchenAI

Once installed, you need to initialize KitchenAI to set up the required migrations and configurations for your project. 

```bash
kitchenai init
```

### 🎬 Example:
![Initialization Process](../../../docs/_static/images/getting-started/init.gif)

This step prepares your environment so you can start building your AI-powered application effortlessly. 🚀

---


BONUS:

For development purposes, you can run the KitchenAI setup to create a default superuser. 

```bash
kitchenai setup
```

admin endpoint can be found at `http://localhost:8000/kitchenai-admin/`.

This will create a default superuser with the email `admin@example.com` and the password `password`.

You’re now installed and ready to start your AI journey with KitchenAI! 🎉  
