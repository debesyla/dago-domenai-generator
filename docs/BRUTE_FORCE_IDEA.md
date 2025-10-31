# Brute Force Domain Generator

## Overview
A systematic domain name generator that produces all possible combinations of characters for a given length range. This approach ensures complete coverage of the domain name space within specified constraints.

## Goals

### Primary Objectives
1. **Exhaustive Generation**: Generate every possible domain name combination within specified parameters
2. **Flexible Character Sets**: Support multiple character type configurations:
   - Numbers only (0-9)
   - Letters only (a-z)
   - Alphanumeric (a-z, 0-9)
   - Hyphen modes:
     - With hyphens (default): Includes domains with and without hyphens
     - Without hyphens: Excludes all hyphens
     - Only hyphens: Must contain at least one hyphen
3. **Length Control**: Allow generation for specific length ranges (e.g., 3-4 characters)
4. **Performance**: Efficiently generate large result sets without memory overflow
5. **Validation**: Ensure generated domains follow DNS naming rules

### Secondary Objectives
- Progress tracking for long-running generations
- Ability to resume interrupted generation sessions
- Export to text format (.txt)
- Domain count estimation before generation

## Technical Solution

### Core Algorithm
Use itertools combinations approach with custom character sets:

```python
import itertools

def generate_combinations(chars, min_len, max_len, include_hyphen=False):
    """Generate all possible combinations for given parameters"""
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(chars, repeat=length):
            domain = ''.join(combo)
            if is_valid_domain(domain, include_hyphen):
                yield domain
```

### Character Sets Definition

```python
CHARACTER_SETS = {
    'numbers': '0123456789',
    'letters': 'abcdefghijklmnopqrstuvwxyz',
    'alphanumeric': 'abcdefghijklmnopqrstuvwxyz0123456789',
}
```

### DNS Validation Rules
1. **Hyphen Constraints**:
   - Cannot start with hyphen
   - Cannot end with hyphen
   - Cannot have consecutive hyphens (--) anywhere in the domain
   
2. **Character Constraints**:
   - Domain names are case-insensitive
   - Only letters, numbers, and hyphens allowed
   - Maximum 63 characters per label (not applicable for short domains)

3. **Numeric Domains**:
   - All-numeric domains are allowed

### Architecture

```
BruteForceGenerator
├── __init__(char_type, min_len, max_len, hyphen_mode, tld)
├── estimate_count() -> int
├── generate() -> Generator[str]
├── generate_to_file(filepath) -> int
├── validate_domain(domain) -> bool
└── get_character_set() -> str

hyphen_mode options: 'with' (default), 'without', 'only'
```

### Implementation Details

#### 1. Character Set Selection
```python
def get_character_set(self, char_type, hyphen_mode):
    base_chars = CHARACTER_SETS[char_type]
    if hyphen_mode in ['with', 'only']:
        return base_chars + '-'
    return base_chars
```

#### 2. Domain Validation
```python
def validate_domain(self, domain):
    # Cannot start or end with hyphen
    if domain.startswith('-') or domain.endswith('-'):
        return False
    
    # Cannot have consecutive hyphens anywhere
    if '--' in domain:
        return False
    
    # Check hyphen mode requirements
    if self.hyphen_mode == 'only' and '-' not in domain:
        return False
    
    return True
```

#### 3. Count Estimation
```python
def estimate_count(self):
    """Estimate total domains before generation"""
    charset_size = len(self.charset)
    total = 0
    for length in range(self.min_len, self.max_len + 1):
        total += charset_size ** length
    
    # Apply rough validation filter based on hyphen mode
    if self.hyphen_mode == 'with':
        total *= 0.90  # Account for hyphen position restrictions
    elif self.hyphen_mode == 'only':
        total *= 0.30  # Only ~30% will have hyphens after filtering
    
    return int(total)
```

#### 4. Memory-Efficient Generation
```python
def generate(self):
    """Generator function to avoid loading all into memory"""
    for length in range(self.min_len, self.max_len + 1):
        for combo in itertools.product(self.charset, repeat=length):
            domain = ''.join(combo)
            if self.validate_domain(domain):
                yield f"{domain}.{self.tld}"
```

### Usage Example

```python
# Generate all 3-4 character .lt domains with hyphens
generator = BruteForceGenerator(
    char_type='alphanumeric',
    min_len=3,
    max_len=4,
    hyphen_mode='with',  # 'with' (default), 'without', or 'only'
    tld='lt'
)

# Estimate count
estimated = generator.estimate_count()
print(f"Estimated domains: {estimated:,}")

# Generate to file
count = generator.generate_to_file('lt_3-4_domains.txt')
print(f"Generated {count:,} domains")

# Or iterate manually
for domain in generator.generate():
    print(domain)

# Example: Generate only domains that contain hyphens
generator_hyphen_only = BruteForceGenerator(
    char_type='alphanumeric',
    min_len=3,
    max_len=4,
    hyphen_mode='only',
    tld='lt'
)
```

## Performance Considerations

### Complexity Analysis
- **3 characters, alphanumeric (36 chars)**: 36³ = 46,656 combinations
- **4 characters, alphanumeric (36 chars)**: 36⁴ = 1,679,616 combinations
- **3-4 characters with hyphen (37 chars)**: ~2M combinations (after validation)

### Optimization Strategies
1. **Generator Pattern**: Use Python generators to avoid memory overhead
2. **Batch Writing**: Write to file in batches for I/O efficiency
3. **Early Validation**: Filter invalid patterns before string construction
4. **Parallel Processing**: For very large sets, split by first character and parallelize

### Memory Usage
- Generator approach: O(1) memory for domain generation
- File writing buffer: ~10MB buffer recommended
- Total memory: <50MB for typical operations

## Integration with Existing System

The brute force generator complements the Markov generator:
- **Brute Force**: Complete coverage, deterministic, smaller lengths
- **Markov**: Creative patterns, larger lengths, probabilistic

Both can be used together:
1. Use brute force for 2-4 character domains
2. Use Markov for 5+ character domains
3. Combine and deduplicate results

## Future Enhancements
1. Resume capability with checkpoint files
2. Progress bar for long-running generations
3. Parallel generation using multiprocessing
4. Domain availability checking integration
5. Custom character exclusion lists (e.g., exclude confusing chars like 0/O)
6. Pattern-based filtering (e.g., pronounceable domains only)
