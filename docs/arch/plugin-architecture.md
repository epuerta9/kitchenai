Below is a **high-level architectural pattern** showing how you can keep **Bentos** and **Plugins** **independent** of each other—yet still **attach** them seamlessly at runtime, without creating circular dependencies. The core idea is to have **a shared interface** (or “contract”) in your framework (KitchenAI core) that both **Bentos** and **Plugins** implement or register against. This way:

- **Bentos** declare **what** capabilities or hooks they provide (e.g., “I’m a RAG pipeline,” “I have `post_llm_generation` hook,” “I support chain-of-thought”).  
- **Plugins** declare **which** hooks or capabilities they **attach** to (e.g., “I run on `post_llm_generation`,” “I need a ‘SalesAgent’ domain,” etc.).  
- A **Plugin Manager** or **Hook Registry** in the KitchenAI core library dynamically **matches** them at runtime—**no** direct import from plugin to bento or vice versa.

Below are the main components and how they fit together:

---

## 1. Shared Core Interface / Hook System (KitchenAI Core)

1. **Hook Definitions**  
   - The core library (KitchenAI) defines a standard set of hook names (e.g., `pre_prompt`, `post_llm_generation`, `final_output`, etc.).  
   - Also defines a “capabilities” concept so a Bento can declare: “I provide RAG retrieval,” “I provide a chain-of-thought pipeline,” etc.

2. **Plugin Registration Decorator** (or function)  
   ```python
   # In kitchenai.core.plugin_system
   def plugin(hook_name: str):
       def wrapper(fn):
           # store fn in a global registry: HOOK_REGISTRY[hook_name].append(fn)
           return fn
       return wrapper
   ```
   - This lives in **KitchenAI core**, not in a bento or a plugin specifically.  
   - Both Bentos **and** Plugins can import this decorator if they need to declare or bind hooks.  

3. **Capability Registry (Optional)**  
   - A place to say: “This Bento implements capabilities [‘rag_retrieval’, ‘basic_chat’].”  
   - A plugin can say: “I only work if `rag_retrieval` is present.”  
   - The system checks alignment at runtime.

---

## 2. Bento Packages (Agent “Bento Boxes”)

### **What the Bento Does:**
- **Implements** certain hooks or has “capabilities” (like “RAG pipeline,” “Sales domain,” “Agent memory,” etc.).  
- **Does NOT** import plugin code.  
- **Exposes** a standard entry point (like `kitchen.py`) that the KitchenAI core can introspect or load metadata from.

### **Example**: `my_sales_bento`  
```python
# my_sales_bento/kitchen.py
from kitchenai.core.capabilities import declare_capabilities

declare_capabilities(["rag_retrieval", "sales_domain"])

# The Bento might define or override some lifecycle logic,
# but it doesn't import any plugin. It relies on the KitchenAI core
# to handle hooking.
```

- The Bento states: “I have the RAG retrieval and a ‘sales_domain’ capability.”  
- At runtime, KitchenAI sees these capabilities and knows which plugins might be relevant.

---

## 3. Plugin Packages

### **What the Plugin Does:**
- **Implements** or **registers** for certain hooks (e.g. `@plugin("post_llm_generation")`) in the KitchenAI core.  
- **Optionally** declares any capabilities it requires or influences (e.g. “Works only if `rag_retrieval` is available”).  
- **Does NOT** import or rely on Bento code. Instead, it only depends on the KitchenAI core’s hook system.

### **Example**: `my_deep_eval_plugin`
```python
# my_deep_eval_plugin/plugin.py
from kitchenai.core.plugin_system import plugin

@plugin("post_llm_generation")
def deep_eval(data: dict) -> dict:
    """
    Evaluate the LLM output for correctness or compliance,
    then store metrics in 'data["evaluation"]'.
    """
    # plugin logic ...
    return data
```

- No mention of a particular Bento. It only uses the core hook name: `post_llm_generation`.

---

## 4. The Plugin Manager or Hook Registry

### **What It Does:**
- **Discovers** all installed bentos and plugins (e.g., by scanning entry points or a config file).  
- **Assembles** a runtime pipeline or workflow for each Bento, injecting the plugin functions at the relevant hooks.

### **Steps**:
1. **Load Bento**: Inspect `kitchen.py` or metadata to see which capabilities or hooks it uses.  
2. **Load All Plugins**: For each plugin, check which hooks it wants and whether it requires specific capabilities.  
3. **Match**:
   - If the bento has `rag_retrieval` capability and the plugin needs `rag_retrieval`, enable that plugin’s hooking.  
   - If the plugin only says it needs `post_llm_generation` (no special capabilities required), then we attach it to the Bento’s pipeline at `post_llm_generation`.  
4. **Build** the final “event chain”:
   ```python
   HOOK_REGISTRY = {
       "pre_prompt": [...list of plugin funcs...],
       "post_llm_generation": [deep_eval, ...],
       ...
   }
   ```

Thus, at runtime, when the Bento triggers `post_llm_generation`, the plugin function(s) are called. **No direct import** is necessary between the Bento and plugin.

---

## 5. No Circular Dependencies

### **Why This Works**:
- **Bentos** depend only on **KitchenAI Core** (for the hooking system or a “declare_capabilities” function).  
- **Plugins** also depend only on **KitchenAI Core** (for the `plugin` decorator / registration).  
- **Neither** directly imports the other. The **Plugin Manager** (part of KitchenAI Core) orchestrates who sees whom at runtime.

**Diagram**:

```
   [my_sales_bento]          [my_deep_eval_plugin]
           |                           |
           v                           v
      (KitchenAI Core) ---> hooking system / plugin manager
```

They both reference the hooking system in KitchenAI, but never each other.

---

## 6. Developer Workflow

1. **Author a Bento** (e.g., “MySalesBento”):
   - It includes `kitchen.py` with `declare_capabilities(...)`.  
   - Possibly it customizes pipeline logic (like retrieving documents, chunking, etc.), but doesn’t mention plugins.
2. **Author a Plugin** (e.g., “DeepEvalPlugin”):
   - `@plugin("<hook_name>")` to indicate which lifecycle event it wants.  
   - Possibly states “requires: rag_retrieval” if it depends on RAG functionality.
3. **Install** both packages into the same environment:
   ```bash
   pip install my_sales_bento
   pip install my_deep_eval_plugin
   ```
4. **Run** KitchenAI:
   ```bash
   kitchenai runserver --module my_sales_bento.kitchen:app
   ```
   - The core sees that we have “sales_domain” + “rag_retrieval” from the bento.  
   - The plugin “deep_eval_plugin” registers for `post_llm_generation`, no special capability needed → it’s attached automatically.  
   - Another plugin might say “I only work if `rag_retrieval` is present,” which also gets attached.  
   - A plugin requiring “marketing_domain” is **not** attached because the bento doesn’t declare “marketing_domain”.

Hence, you get a **runtime-constructed pipeline** that includes only the relevant plugin(s) for that Bento.

---

## 7. Summarizing the Approach

1. **KitchenAI Core** 
   - Houses the hooking system (`plugin()` decorator), a **capability registry** (optional), and a **Plugin Manager**.  
2. **Bentos** 
   - Each bento is a self-contained Django app or Python package.  
   - Declares **capabilities** or overrides pipeline steps, but does **not** import plugin code.  
3. **Plugins** 
   - Each plugin is a separate package that registers for hooks.  
   - May declare optional **capability requirements**.  
   - Never imports or references a specific Bento directly.  
4. **Automatic Matching** 
   - At runtime, the **core** merges everything.  
   - If a plugin’s required capabilities are present in the bento, the plugin’s hook is attached.  
   - No direct dependency from plugin → bento or bento → plugin.

This yields a **clean, decoupled** architecture where **Bentos** and **Plugins** are truly **pluggable**—all they share is the **KitchenAI** interface, and a small set of **runtime metadata** (hooks + capabilities).

---

### Final Takeaway

> **To avoid circular dependencies** between **Bentos** and **Plugins**, **both** should depend on **KitchenAI core**—a neutral “meeting place” that defines hooks, capabilities, and a plugin manager. **Bentos** declare what they can do (capabilities), **plugins** declare what they need or which hooks they attach to, and the **core** merges them at runtime. This ensures the Bento is authored with the appropriate abilities, while the right plugins attach automatically—without either side directly referencing the other.