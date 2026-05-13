# behavioral-cloning-decision-mechanism
Decision mechanism with behavioral cloning for game agent - AI project
🐍 MimicSnake AI
MimicSnake AI is an interactive Python-based game that demonstrates the lifecycle of a Machine Learning model. The project allows users to play a snake game, collect behavioral data, and train an AI agent that "mimics" their playstyle using Random Forest Classifier.

🚀 Features
Data Collection: Record your own movements relative to the food.

Model Training: Train a Random Forest model with one click.

AI Racing: Race against an AI that has learned from your behavior.

Difficulty Levels: Easy, Medium, and Hard modes to test your training quality.

Real-time Metrics: Visual accuracy bar showing how well the model learned.

🛠 Methodology
The project uses Supervised Learning to predict the snake's next move.

Inputs (Features): Relative distance to food (dx, dy), Manhattan distance, and normalized direction vectors.

Algorithm: RandomForestClassifier from scikit-learn.

Inference: The model predicts the move (UP, DOWN, LEFT, RIGHT) based on real-time game state coordinates.
💻 Installation & Setup
Clone the repository:

Bash
git clone https://github.com/azrabaltali/behavioral-cloning-decision-mechanisim.git
cd mimicsnake-ai
Install dependencies:

Bash
pip install pygame pandas scikit-learn numpy
Run the game:

Bash
python main.py
📦 How to Play
Click Data Collect and eat as many fruits as possible. (Press ESC to save and return to menu).

Click Train Model to process your data.

Once the Accuracy Bar appears, click Start Race to compete with your AI mimic!
