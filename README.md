# Dago Domenai Generator

A comprehensive toolkit for generating domain name lists using multiple algorithmic approaches. This project provides various domain generation strategies including Markov chain-based generation, brute-force combinations, and pattern-based creation, designed for domain availability analysis and research.

## 🚀 Features

- **Multiple Generation Methods**:
  - Markov Chain Generator: Trained on real domain corpora for realistic name generation
  - Brute Force Generator: Exhaustive combinations of characters within specified lengths
  - Pattern Generator: Regex-like pattern matching for structured domain creation
  - Random Generator: Weighted random combinations

- **Flexible Output**: Generates `.txt` files compatible with external domain analysis tools
- **CLI Interface**: Simple command-line interface for easy integration
- **Progress Tracking**: Built-in progress indicators and ETA calculations
- **Memory Efficient**: Handles large-scale generation without memory overflow

## 📋 Requirements

- Python 3.8+
- Dependencies: See `requirements.txt` (to be created)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dago-domenai-generator.git
cd dago-domenai-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Basic Usage

```bash
# Generate domains using Markov chains
python src/main.py markov --order 3 --count 10000

# Generate brute-force combinations
python src/main.py brute --min 2 --max 4

# Run all generators
python src/main.py all
```

### Markov Generator

Train on a corpus of real domains and generate new ones:

```bash
python src/main.py markov \
  --input assets/input/real_domains.txt \
  --order 3 \
  --count 50000 \
  --output assets/output/markov_generated.txt
```

### Brute Force Generator

Generate all possible combinations:

```bash
python src/main.py brute \
  --min 2 \
  --max 4 \
  --charset alphanumeric \
  --output assets/output/brute_generated.txt
```

### Combining Outputs

```bash
# Combine all generated domains
cat assets/output/*.txt > assets/output/all_domains.txt

# Remove duplicates and sort
sort assets/output/all_domains.txt | uniq > assets/output/unique_domains.txt
```

## 📁 Project Structure

```
dago-domenai-generator/
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── OVERVIEW.md
│   ├── MARKOV_IDEA.md
│   ├── BRUTE_FORCE_IDEA.md
│   └── ROADMAP.md
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # CLI entry point
│   │
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── markov_generator.py     # Markov-based generation
│   │   ├── brute_generator.py      # Brute-force combinations
│   │   ├── pattern_generator.py    # Pattern-based generation
│   │   └── random_generator.py     # Random generation
│   │
│   └── utils/
│       ├── io_utils.py             # File I/O helpers
│       ├── markov_utils.py         # Markov utilities
│       └── progress_utils.py       # Progress tracking
│
└── tests/
    ├── test_markov.py
    ├── test_brute.py
    └── test_io.py
```

## 🔧 Development

### Setting up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Run linting
flake8 src/

# Run type checking
mypy src/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is intended for research and educational purposes. Please respect domain registration policies and applicable laws when using generated domain lists. The authors are not responsible for any misuse of this software.

## 📚 Documentation

Detailed documentation for each generator can be found in the `docs/` directory:

- [Project Overview](docs/OVERVIEW.md)
- [Markov Chain Generation](docs/MARKOV_IDEA.md)
- [Brute Force Generation](docs/BRUTE_FORCE_IDEA.md)

## 🗺️ Roadmap

Future enhancements planned:

- AI-based domain generation
- Semantic word combination generator
- TLD-specific generation rules
- Integration with WHOIS APIs
- Web-based interface
- Performance optimizations for large-scale generation

---

**Made with ❤️ for the domain research community**