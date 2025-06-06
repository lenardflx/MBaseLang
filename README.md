# MBaseLang

**MBaseLang** is a math-first programming language.  
This project was created as a small learning experiment to explore language design, interpreters, and symbolic math features.

It is currently implemented in Python. A minimal interpreter written in Rust is provided in the `rust/` directory as an experimental rewrite.

---

## Current Features

- Custom numeric base literals (`b2@1010`, `b16@FF`, etc.)
- User-defined functions with proper scoping and `ret`
- Block-based control flow: `loop`, `while`, labeled `@block` with `break`/`continue`
- Math operations on base-aware numbers (`+`, `-`, `*`, `/`)
- Input/output with `in()` and `out(...)`
- String interpolation using `{}` inside strings
- Basic symbolic handling via `BaseLiteral` objects

---

## Run It

You can run MBaseLang in two ways:

### 1. Run the REPL

```bash
python run.py
```

### 2. Run a File

```bash
python run.py examples/1.mbl
```

### 3. Run the Rust Rewrite

Build the Rust project with Cargo and pass a `.mbl` file:

```bash
cargo run -p mbaselang_rust -- examples/1.mbl
```
