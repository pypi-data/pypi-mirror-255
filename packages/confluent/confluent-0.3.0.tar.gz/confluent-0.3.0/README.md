# confluent
In times of distributed systems and en vogue micro-architecture it can get quite cumbersome to keep constants that are required by several components up-to-date and in sync. It can get especially hard when these components or services are written in different languages. *confluent* targets this issue by using a language neutral YAML configuration that lets you generate language specific config files in the style of classes and structs.

## Example
Alright, after all this confusing hipster-talk, lets just have a look at a simple example to see what *confluent* can do for you.

### Input (readme-config.yaml)
```yaml
languages:
  - type: typescript
    property_naming: screaming_snake
    export: esm

  - type: python
    file_naming: snake
    property_naming: screaming_snake

  - type: c
    file_naming: snake
    property_naming: pascal

properties:
  - type: string
    name: opener
    value: Hello World
```

### Output (readme-config.ts)
```typescript
export const ReadmeConfig = {
    OPENER: 'Hello World',
} as const;
```

### Output (readme_config.py)
```python
class ReadmeConfig:
    OPENER = 'Hello World'
```

### Output (readme_config.h)
```c
#ifndef README_CONFIG_H
#define README_CONFIG_H

/* Generated with confluent v0.3.0 (https://pypi.org/project/confluent/). */
const struct {
    char* Opener;
} ReadmeConfig = {
    "Hello World",
};

#endif /* README_CONFIG_H */
```

## Currently supported languages
- [x] Java
- [x] JavaScript
- [x] TypeScript
- [x] Python
- [x] C
- [x] Go

## Installation
```bash
python3 -m pip install confluent
```

## Configuration
For detailed configuration information, please check [example/test-config.yaml](https://github.com/monstermichl/confluent/blob/main/example/test-config.yaml). All possible values are described there.

## Usage
### Commandline
```bash
python3 -m confluent -c test-config.yaml -o generated
# For more information run "python3 -m confluent -h".
```

### Script
```python
from confluent import Orchestrator

# Create Orchestrator instance from file.
orchestrator = Orchestrator.read_config('test-config.yaml')

# Write configs to 'generated' directory.
orchestrator.write('generated')

# Distribute configs (if required).
orchestrator.distribute()
```

## How to participate
If you feel that there's a need for another language, feel free to add it. For detailed information how to add support for a new language, please refer to [README.md](https://github.com/monstermichl/confluent/tree/main/misc/language_support/README.md).
