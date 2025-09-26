# 🎈 Hello-Balloons - Balloon Game

A fun web-based balloon navigation game where you collect dollars while avoiding spikes! Built with Python Flask backend and interactive web interface.

![Game Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-green)
![License](https://img.shields.io/badge/License-MIT-blue)

## 🎮 Game Overview

Navigate your balloon (O) through the map to collect dollars ($) while avoiding deadly spikes (*)! Each dollar collected spawns a new spike at the previous dollar location, making the game progressively more challenging.

### 🎯 Game Features

- **Interactive Web UI**: Play directly in your browser
- **Bot Algorithms**: Watch AI bots play with different strategies
- **Bot Builder**: Create and test your own bot algorithms
- **Speed Controls**: Multiple speed settings from Slow to Godspeed
- **Score System**: Track your best scores and compete on leaderboards
- **Real-time Gameplay**: Smooth animations and responsive controls

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Flask 2.0+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Bejjoeqq/Hello-Balloons.git
cd Hello-Balloons
```

2. Install dependencies:
```bash
pip install flask
```

3. Run the game:
```bash
python web_app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## 🎮 How to Play

### Human Player Mode
- **W, A, S, D** - Move your balloon
- **Objective**: Collect dollars ($) while avoiding spikes (*)
- **Challenge**: Each dollar collected creates a spike at the previous location

### Bot Demo Mode
- Watch pre-built AI bots play automatically
- Choose from multiple bot algorithms
- Adjust playback speed for better observation

### Bot Builder Mode
- Write your own Python bot algorithm
- Test your bot in real-time
- Save and share your creations

## 🤖 Bot Development

### Creating a Bot

Your bot must implement the `checkBot(hero)` function:

```python
def checkBot(hero):
    # Get current position
    pos = hero.getLocation()  # Returns [x, y]
    
    # Get dollar location
    dollar = hero.findLocationDollar()  # Returns [y, x]
    
    # Your logic here...
    
    return 'w'  # Return: 'w', 'a', 's', or 'd'
```

### Available Bot Methods

- `hero.getLocation()` - Get balloon position [x, y]
- `hero.findLocationDollar()` - Get dollar position [y, x]
- `hero.getMove()` - Get current move direction
- `hero.getMap()` - Get full map state

### Built-in Bot Algorithms

The game includes several pre-built bots with different strategies:
- **Champion Bot**: Advanced pathfinding algorithm
- **Perfect Score Bot**: Optimized for high scores
- **Quantum Neural Bot**: AI-powered decision making
- **And more!**

## 📁 Project Structure

```
Hello-Balloons/
├── web_app.py              # Flask web server
├── main.py                 # CLI version entry point
├── app/
│   ├── __init__.py         # App initialization
│   ├── hero.py             # Hero/Balloon class
│   ├── map.py              # Game map logic
│   ├── guide.py            # Game utilities
│   ├── start.py            # Game state management
│   ├── prompt.py           # Input handling
│   └── bot/
│       ├── __init__.py     # Bot loader
│       ├── template.py     # Bot template
│       └── *.py            # Individual bot algorithms
├── templates/
│   ├── index.html          # Main menu
│   ├── game.html           # Human player interface
│   ├── bot_demo.html       # Bot demonstration
│   └── bot_builder.html    # Bot creation interface
└── README.md               # This file
```

## 🛠️ Development Status

**🚧 Currently in active development**

- ✅ Core gameplay mechanics
- ✅ Web interface
- ✅ Bot system integration
- ✅ Custom bot builder
- 🔄 Enhanced AI algorithms
- 🔄 Multiplayer features
- 🔄 Persistent online leaderboards

## 💾 Data Storage

**Important**: This game currently uses **local storage only**:
- All scores and progress are stored in your browser
- Data may be lost if you clear browser data
- No online sync or backup currently available

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Adding Bot Algorithms

1. Create a new Python file in `app/bot/`
2. Implement the required `NAME` variable and `checkBot(hero)` function
3. Test your bot using the Bot Builder interface
4. Submit a pull request with your bot algorithm

### Bug Reports & Feature Requests

- Open an issue on GitHub
- Provide detailed description and steps to reproduce
- Include browser information for web-related issues

### Development Setup

```bash
# Clone the repo
git clone https://github.com/Bejjoeqq/Hello-Balloons.git

# Create development branch
git checkout -b feature/your-feature-name

# Make changes and test
python web_app.py

# Submit pull request
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AI-Assisted Development**: This project was developed with assistance from AI tools for code generation, debugging, and documentation
- Game concept inspired by classic navigation puzzles
- Thanks to all contributors and bot algorithm creators

## 📧 Contact

- **GitHub**: [Bejjoeqq](https://github.com/Bejjoeqq)
- **Repository**: [Hello-Balloons](https://github.com/Bejjoeqq/Hello-Balloons)

---

*Made with ❤️ and 🤖 AI assistance*