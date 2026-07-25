# Portals

> A Portal is any place where information enters the TouchDesigner universe.

## Example Portals

```bash
├── Audio Device In
├── Movie File In
├── Video Device In
├── OSC In
├── MIDI In
├── Kinect
├── Webcam
├── NDI
├── Serial
└── TCP/IP
```

# Audio Portal Example

```yaml
portal:
  name: Live Guitar

operator:
  Audio Device In CHOP

domain:
  audio

contains:
  continuous waveform

time:
  real-time

semantic_meaning:
  "The performer enters the system."
```

# Layers

> These are the immediate primitives that naturally surround the portal.

## Lexicon

```yaml
lexicon:

  acquisition:

    Audio Device In

    Audio File In

  normalization:

    Null

    Math

    Filter

    Lag

    Limit

  analysis:

    Analyze

    Audio Spectrum

    Spectrum

    Envelope

    Slope

    Logic

  routing:

    Select

    Rename

    Merge

    Shuffle

  visualization:

    Trail

    CHOP to TOP
```

## Gestures

```yaml
Gesture: 
  Loudness: |

        Audio Device In

        ↓

        Analyze

        ↓

        Math

        ↓

        Null

    Produces: 
      output: audio_level

```

> This is probably the most common gesture in TouchDesigner.

```yaml
Gesture: 
  Smooth Energy: |
        Audio Device In

        ↓

        Analyze

        ↓

        Filter

        ↓

        Math

        ↓

        Null
    
    Produces: 
      qualities:
        - breathing
        - continuous
        - organic
```

```yaml
Gesture: 
  Spectral Decomposition: |
        Audio Device In

        ↓

        Audio Spectrum

        ↓

        Math

        ↓

        Null
    Produces:
      outputs:
        - bass
        - mid
        - trebel
```

```yaml
Gesture:
  Attack Detection: |
        Audio Device In

        ↓

        Analyze

        ↓

        Slope

        ↓

        Logic
    
    Produces: 
      output:
        - transient_events
```

> Notice the Attack Detection Gesures is event driven, not continuous signal, so offers a different class of expressive possibilities

```yaml
Gesture:
  Envelope Following: |
        Audio Device In

        ↓

        Envelope

        ↓

        Math

    Produces: 
      output:
        - articulation
```

## Idioms

```yaml
Breathing:
  Characteristics:
    - RMS
    - filtering
    - slow response
  Visual Consequence: 
    - slow expansion
    - glowing
    - displacement

Pulse:
  Characteristics:
    - peaks
    - attacks
    - onset
  Visual Consequence: 
    - flashes
    - particle emission 
    - scaling

Resonance: 
  Characteristics: 
    - narrow frequency bands
  Visual Consequence: 
    - localized movement
    - harmonic colors
    - oscillation


Rhythm:
  Characteristics:
    - repeated transients
  Visual Consequence:
    - stepping 
    - sequencing
    - triggering

Silence:
  Characteristics:
    absense:
      - energy
      - duration
      - decay
  Visual Consequence: 
    - fading
    - reconstruction
    - settling
```

## Traversals

> Once we've extracted one kind of information, where can it naturally go?

Let's say a `Gesture` outputs `audio_level`: Where can it travel?

```bash
audio_level

├── brightness

├── displacement

├── bloom

├── particle emission

├── camera motion

├── feedback opacity

├── simulation speed

├── geometry scale

├── color temperature

└── fog density
```

Let's say a `Gesture` outputs `bass_energy`: Where can we traverse **to** from that output?

```bash
bass

├── gravity

├── slow camera drift

├── fluid pressure

├── mesh inflation

└── particle size
```

```bash
treble

├── sparkle

├── edge glow

├── turbulence

├── grain

└── noise frequency
```

> Traversals are expressive tendencies based on outputs from some other Layer

## Composition

> A complete human readible manifest of the intent of the work

### Example

```yaml
composition:

  title:

    Monk Breathes

portal:

  guitar

idioms:

  breathing

  memory

  emergence

traversals:
    RMS

    ↓

    displacement

    sustain

    ↓

    feedback

    silence

    ↓

    portrait reconstruction
```

## Semantic Features

> What we mean by the words we choose to express ourselves which help make explicit our creative intent

**Between the raw signal and the artistic idiom is a semantic interpretation.**

### Example

```bash
waveform

↓

RMS

↓

"energy"

↓

Breathing
```

### Example

```bash
spectrum

↓

centroid

↓

"brightness"

↓

Sparkle
```

> the quoted words are neither signal-processing terms nor visual effects. They're perceptual features. They describe qualities that humans recognize across domains: we hear a phrase as "heavy," and we might render it with slower, denser motion; we hear it as "fragile," and render it with delicate, dissolving particles.

# Compiler Architecture for Creative Systems

Not because we want to "compile" TouchDesigner, but because compiler design gives us an incredibly elegant way to separate concerns:

```bash
TouchDesigner (.toe)
          │
          ▼
Introspection Pass
          │
          ▼
graph.yaml
          │
          ▼
Semantic Analysis Pass
          │
          ▼
architecture.yaml
          │
          ▼
Pattern Language Pass
          │
          ▼
composition.yaml
```

**Each pass adds meaning without losing the previous layer.**

> That separation is powerful because it means SCHEMA.md doesn't need to know anything about connectors, and the connector extractor doesn't need to know anything about "breathing" or "memory." Those become independent, composable layers. This whole concept abstracts the tech stack into a system type like Max/MSP, Unreal Engine Blueprints, Houdini networks, or even modular synthesizers which are graphs of transformations carrying signals through expressive spaces. We're trying to outline a language for reasoning about computational art itself by separating these concerns: structure, semantics, and intention. 

## Instrospection

TouchDesigner exposes its entire project model through Python.

That means a script can ask things like:

```python
for op in root.findChildren():
    print(op.inputConnectors)
```

