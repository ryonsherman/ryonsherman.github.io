title: Custom Firmware — Building a Programming Language Stack for Arduino Nano
description: A complete language stack from scratch — BASIC compiler, custom assembly, bytecode VM, and Arduino firmware — all written from scratch to learn how computers actually work.
date: 2026-07-02
---

I built a complete programming language stack for an Arduino Nano. A BASIC compiler, a custom assembly language, a two-pass assembler, a stack-based bytecode VM, and firmware that runs on the ATmega328P — all from scratch. No parser generators, no VM libraries, no shortcuts.

## The full stack

```
BASIC source (.bas)             10 LET A = A + 1
    ↓  compiler.py
Assembly language (.asm)        load A / push 1 / add / store A
    ↓  assembler.py
Bytecode binary (.bin)          08 00 01 01 04 09 00
    ↓  either:
    ├── emulator.py (Python VM on PC)
    └── uploader → serial → Arduino firmware (C++ VM)
```

The compiler outputs assembly text, not bytecode directly. This was intentional — you can inspect the generated assembly and understand exactly what the compiler is doing before the assembler turns it into opaque bytes.

The BASIC dialect supports LET, PRINT, INPUT, IF/THEN/GOTO, FOR/NEXT/STEP, GOSUB/RETURN, END, and full arithmetic expressions with operator precedence. A program like this compiles down to 23 bytes of bytecode:

```basic
10 LET A = 0
20 LET A = A + 1
30 PRINT A
40 IF A < 10 THEN GOTO 20
50 END
```

## Why a stack machine

Three architectures were on the table: a register machine (complex decode, lots of bits for register selection), a stack machine (simple decode, operands always on top of stack), or transpiling to C (no firmware needed but hides the hardware layer).

The stack machine won because instructions are shorter (no register fields), decode logic is simpler (opcode → action, no operand selection), and expression evaluation maps directly to stack operations (`a + b * c` becomes `push a, push b, push c, mul, add`). The tradeoff: more instructions per program and genuinely awkward temporary value management in hand-written assembly.

The instruction set ended up at 21 opcodes across seven categories: stack operations, arithmetic, variables, comparison, control flow, I/O, and subroutines. All values are 16-bit signed integers — 8-bit felt too constrained (-128 to 127), and 32-bit wastes too much of the Nano's 2KB of RAM.

## The tools

The **lexer** is a character-by-character tokenizer that recognizes keywords (LET, PRINT, IF, FOR, etc.) against a set. Multi-character operators (`<=`, `>=`, `<>`) peek ahead one character.

The **parser** is recursive descent — one function per grammar rule. `_expr_addsub()` handles `+` and `-`, `_expr_term()` handles `*` and `/`, `_expr_factor()` handles numbers, variables, parentheses, and unary minus. Operator precedence emerges from the call hierarchy: `addsub → term → factor`. Higher-precedence operators are deeper in the call chain.

The **assembler** is two-pass. Pass one finds all labels and records their byte addresses while tracking instruction sizes. Pass two encodes instructions and resolves label references to addresses. Each instruction has a known byte length (1, 2, or 3 bytes). A single off-by-one in pass one shifts every subsequent label by one byte, breaking all jump targets.

The **emulator** runs on the PC with an optional trace mode that prints every instruction — address, mnemonic, operand, and full stack state — making opaque execution readable:

```
[0x0000] PUSH   0            stack: [0]
[0x0002] STORE  A            stack: []
[0x0004] LOAD   A            stack: [1]
[0x0006] PUSH   1            stack: [1, 1]
[0x0008] ADD               stack: [2]
[0x0009] STORE  A            stack: []
```

## Making it fit in 2KB

The ATmega328P has 2KB of RAM. Every byte matters. The memory budget was:

| Component | Size |
|---|---|
| Program storage (bytecode) | 1024 bytes |
| Data stack (64 × int16) | 128 bytes |
| Return stack (32 × int16) | 64 bytes |
| Variables (26 × int16) | 52 bytes |
| Serial line buffer | 64 bytes |
| **Subtotal** | **1332 bytes** |
| Free | ~519 bytes |

The firmware itself compiled to 3,278 bytes of flash — 10% of the 32KB program memory.

## The serial protocol

The Arduino receives bytecode over a single UART pin. The protocol is minimal: two sync bytes (0xAA, 0x55), a 2-byte program length, then the program bytes. The firmware stores them in RAM, resets the VM state, and starts executing. PRINT and PRINTS output over serial. INPUT reads a line. HALT sends "DONE" and waits for the next upload.

The sync bytes prevent the receiver from interpreting random noise as valid data. This mattered — opening a serial port from Python asserts the DTR line, which resets the Arduino. The boot message gets sent while the host is still opening the port and gets lost. The uploader has to wait 2 seconds after opening before sending the program.

## The bugs that made it real

The first version of unary minus compiled `-value` as `push value; push 0; sub` — which computes `value - 0 = value`, not `0 - value = -value`. This made every negative STEP in a FOR loop positive. Countdown loops ran upward forever. It took two sessions to find.

FOR/NEXT without STEP was initially missing. The compiler required STEP on every loop. Hours of debugging revealed it was a missing default case — STEP 1 should be implicit when no STEP is given.

The bare-metal firmware attempt told a different story. Stripping the Arduino core reduced flash usage from 3,278 bytes to 1,804 bytes — a 45% reduction. The UART registers were straightforward to program. But the CH340 USB-serial chip on the Nano clone has inconsistent timing requirements. After the DTR reset and bootloader timeout, the CH340 needs a stabilization period before the host can reliably receive data. The code is correct — verified at the assembly level — but output arrives inconsistently across runs. The issue lives in the interaction between the CH340 driver, macOS serial port timing, and the hardware reset sequence.

## What I Learned

- **Fetch-decode-execute is not an abstraction** — It's literally what happens on every instruction at every level, from the laptop's x86 to the Nano's AVR to a toy VM. Implementing it yourself makes that concrete in a way no textbook can.

- **Recursive descent parsing maps directly to grammar rules** — One function per rule. Operator precedence is just function call order. `_expr_addsub()` calls `_expr_term()` which calls `_expr_factor()`. Multiplication binds tighter than addition because `_expr_term` is deeper in the call chain. That's the entire mechanism.

- **The SUB operand order bug was inevitable** — A stack machine's SUB pops the top value (the second operand) and the second value (the first operand). Natural reading order (`PUSH 10, PUSH 3, SUB` = 7) works for literals but breaks for unary negation. `0 - value` requires pushing 0 first, then the value. Getting this wrong caused the longest debugging session in the project.

- **2KB RAM forces real tradeoffs** — You can't add another buffer. You can't use dynamic allocation. The memory budget table was a real document, not a theoretical exercise. Every allocation had to be justified.

- **The CH340 taught me about hardware debugging** — The UART init code was correct. The disassembly was correct. The bug lived in the USB-serial chip's power-on timing behavior, not in the AVR code. Bare-metal debugging requires thinking at every layer simultaneously, from register setup to driver timing.

- **A two-pass assembler is the right complexity for this scale** — Labels can be referenced before they're defined. The first pass only measures instruction sizes; the second pass fills in addresses. Forward references are resolved without a linker because there's no separate compilation. The simplicity is the elegance.

- **Test on the emulator first** — Every bug found on the Nano was harder to diagnose than the same bug on the emulator. The trace mode (printing every instruction with stack state) was the single most valuable debugging tool in the entire project.
