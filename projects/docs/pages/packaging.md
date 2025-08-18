# Packaging 101 — Everything is a package

This page explains the **package-based** architecture we use to share and reuse data (Goods, Processes, Systems, ..). Think **npm/pip**, but for LCA. A package is just a small JSON manifest plus its data; a **resolver** installs what you ask for and writes a **lockfile** for reproducibility.


## “leaf” package: The smallest unit

A leaf has **no dependencies**. Example: the periodic table used for conserved properties.

```json
{
  "name": "periodic-table",
  "organization": "CIRAIG",
  "version": "21.3.0",
  "dependencies": {}
}
```

- Importing this brings only its own objects (elements, symbols, atomic masses).
- Other packages **depend** on it instead of re-embedding it.


## A meta-package with extras: `CIRAIG/base`

In real-life scenarios, it's common that we need a lot of dependencies, we could then import a **meta-package**, like `base`: it mostly declares **dependencies** you’ll want in most projects. It also exposes **extras** so you can tailor size.

```json
{
  "name": "base",
  "organization": "CIRAIG",
  "version": "1.3.0",
  "extras": {
    "lca-core": ["CIRAIG/periodic-table@^21", "CIRAIG/units@^4", "CIRAIG/core-taxonomies@^3"],
    "regions": ["CIRAIG/regions-topology@^2"],
    "units": ["CIRAIG/units@^4"],
    "agri": ["CIRAIG/agri-goods@^2", "CIRAIG/agri-processes@^1"],
    "metals": ["CIRAIG/metals-goods@^1", "CIRAIG/metals-processes@^1"]
  },
  "default_extras": ["lca-core","regions", "units"]
}
```

- **extras** are opt-in bundles (pick only what you need).
- **default_extras** are pulled if you don’t specify extras explicitly.

These **meta-package** allow you to start fast, thanks to the community members that have more experiences and share ready-to-use toolkit already thought for real-life LCA analysis and updated over time (like the `CIRAIG` meta-packages). 


## A real project (study) that depends on packages

Day-to-day analysis is also a package. It declares what it needs and stays reproducible via a lockfile.

```json
{
  "name": "life_cycle_analyses_of_masks_and_their_end_of_life",
  "version": "1.0.0",
  "dependencies": {
    "CIRAIG/base": { 
      "version": "^1.0.0", 
      "extras": ["lca-core","units"]
    },
    "international-health-organisation/COVID19-database": "^3.2.0"
  }
}
```

- The resolver fetches `base` + selected extras, plus any other deps.
- You get only what you asked for and don’t get swamped with unnecessary data. 
- You get a self-consistent, reproductible, runnable set


## How installs work (in 10 seconds)

1. You author a `dependencies.json` like the above
2. You run the command 

```code
marcot install
```

How does this command works ?

1. **Resolve**: the tool picks exact versions.  
3. **Lock**: it writes `dependencies.lock.json` (pinning versions for reusabilities).
4. **Import**: data is installed into your workspace.

!!! warning
    Always keep the **lockfile** in your repo to guarantee identical results later.


## Best practices

- Start every study with `CIRAIG/base` (pick only the extras you need).  
- Keep **references** (periodic table, units, regions) as dependencies—don’t recreate the wheel!  
- Pin results with the **lockfile**.
- Prefer smaller packages, no need to import things you don't use. 
- Control and keep trace of **provenance & license** to anything you publish.

---

## Glossary

- **Package**: a named, versioned set of LCA data (Good/Process/System, ..).  
- **extras**: optional dependency groups inside a meta-package.  
- **resolver**: tool that expands your manifest into exact versions + closure (ie: `marcot install`).  
- **lockfile**: frozen record of what was installed (for reproducibility).