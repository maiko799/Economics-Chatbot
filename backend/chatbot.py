import nltk
from nltk.tokenize import word_tokenize
import random

nltk.download('punkt')

# Load topics and quizzes dynamically
def load_economics_data(filename):
    topics = {}
    quizzes_by_topic = {}
    current_topic = None
    quiz_buffer = {}

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_topic = line[1:-1].lower()
                quizzes_by_topic[current_topic] = []
            elif line.startswith('Q:'):
                quiz_buffer = {'question': line[3:].strip()}
            elif line.startswith('A:'):
                quiz_buffer['answer'] = line[3:].strip().lower()
            elif line.startswith('C:'):
                quiz_buffer['choices'] = [choice.strip() for choice in line[3:].split('|')]
                quizzes_by_topic[current_topic].append(quiz_buffer)
            elif current_topic and line and current_topic not in topics:
                topics[current_topic] = line

    return topics, quizzes_by_topic

topics, quizzes_by_topic = load_economics_data("chat.txt")
used_questions = set()


# Utility functions
def tokenize_input(user_input):
    return [w.lower() for w in word_tokenize(user_input)]

def find_topic(user_input):
    user_input = user_input.lower()
    for topic in topics:
        if topic in user_input or user_input in topic:
            return topic
    return None

def ask_quiz_question():
    # Flatten and shuffle all quiz questions
    all_questions = []
    for topic, quizzes in quizzes_by_topic.items():
        for q in quizzes:
            key = f"{q['question'].lower()}|{topic}"
            if key not in used_questions:
                all_questions.append((topic, q, key))
    if not all_questions:
        print("🎉 You've completed all available quiz questions for this session!")
        return

    topic, quiz, key = random.choice(all_questions)
    used_questions.add(key)

    print("\n🧠 Quiz Time!")
    print("Topic:", topic.title())
    print("Q:", quiz['question'])

    choices = quiz['choices']
    random.shuffle(choices)
    for idx, choice in enumerate(choices):
        print(f"{idx + 1}. {choice}")

    correct_answer = quiz['answer']
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        try:
            user_input = int(input("Enter the number of your answer: "))
            selected = choices[user_input - 1].lower()
            if correct_answer in selected:
                print("✅ Correct!\n")
                return
            else:
                attempts += 1
                if attempts < max_attempts:
                    print("❌ Try again.")
                else:
                    print(f"❌ The correct answer was: {correct_answer}\n")
        except (ValueError, IndexError):
            print("⚠️ Please enter a valid option number.")

# Main Chatbot
def econ_chatbot():
    print("📘 Welcome to EconBot!")
    print("Ask me about the following economics topics, type 'quiz' to test your knowledge, or 'exit' to leave:")
    print("GDP, Inflation, Unemployment, Monetary or Fiscal Policy, Aggregate Demand, Supply and Demand, Elasticity, Utility Maximization, ")
    print("Opportunity Cost, PPF, Game Theory, Perfect Competition, Monopoly, Oligopoly, Price Discrimination, Cost Structure,Break even analysis, SWOT analysis, Market Failure")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Keep studying economics. 💼")
            break
        elif user_input.lower() == "quiz":
            ask_quiz_question()
        else:
            topic = find_topic(user_input)
            if topic:
                print(f"📚 {topics[topic]}\n")
            else:
                print("🤖 I didn't catch that topic. Try asking about GDP, inflation, game theory, etc.\n")

econ_chatbot()