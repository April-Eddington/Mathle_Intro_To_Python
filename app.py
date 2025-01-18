"""
Welcome to Mathle! 
Created by: April Eddington for Sophia 01/2025
This onyl has addition problems for right now as this was a school project. This may be expanded in the future
How to play:
1. You'll see a math problem like "5 + _ = 12"
2. Try to guess what number goes in the blank
3. After each guess, you'll get a hint:
   - Green means you got it right!
   - Yellow means the number appears in the answer
   - Red means try a different number
4. You have 5 tries to solve it

Have fun and improve your addition skills!
"""

from flask import Flask, render_template, request, jsonify, session
import random
import secrets

#Start up the fun game of "MATHLE" <-- Couldn't think of a better name
app = Flask(__name__)
#This keeps player information safe - Basically, helps with tracking individual players
app.secret_key = secrets.token_hex(16)

def generate_equation():
    """
    Creates a random math problem for the player to solve. Just addition for not  
    """
    # Pick two random numbers between 1 and 99
    first_number = random.randint(1, 99)
    answer = random.randint(1, 99)
    
    #Calculate what the total should be
    total = first_number + answer
    
    #reate the equation with a blank space
    problem = f"{first_number} + _ = {total}"
    
    return problem, answer

@app.route('/')
def index():
    """
    This is what players see when they first open the game.
    It creates a new math problem and sets up everything they need to play.
    """
    #Make a new problem for the player
    problem, answer = generate_equation()
    
    #Set up the game rules and keep track of player's progress
    session['correct_answer'] = answer
    session['attempts'] = 0  #Start with 0 tries
    session['max_attempts'] = 5  #Player gets 5 tries
    session['game_over'] = False  #Game is just starting
    session['equation_numbers'] = [int(n) for n in str(answer)]  #Remember the answers digits
    
    #Show the game page to the player
    return render_template('index.html', 
                         equation=problem, 
                         attempts=session['attempts'], 
                         max_attempts=session['max_attempts'])

@app.route('/guess', methods=['POST'])
def check_guess():
    """
    This handles what happens when a player makes a guess.
    It checks if they're right and gives them hints to help them solve the problem.
    """
    try:
        #Get the player's guess and make sure it's valid
        player_guess = int(request.json['guess'])
        if not 1 <= player_guess <= 99:
            return jsonify({'error': 'Please pick a number between 1 and 99'})
        
        #Get the right answer and count this try
        correct_answer = session['correct_answer']
        session['attempts'] = session.get('attempts', 0) + 1
        
        #Check if they got it right
        if player_guess == correct_answer:
            feedback = 'green'  # Woohoo! They got it!
            message = 'Correct! You solved the equation!'
            session['game_over'] = True
        elif str(player_guess) in str(correct_answer):
            feedback = 'yellow'  # Some digits match
            message = 'Some of these numbers are in the answer!'
        else:
            feedback = 'red'  # Not quite right! 
            message = 'Try again!'
        
        #Check if they've used all their tries, if so, end the game show th e answer
        if session['attempts'] >= session['max_attempts'] and player_guess != correct_answer:
            session['game_over'] = True
            message = f'Game Over! The answer was: {correct_answer}'
        
        #Let them know how they did
        return jsonify({
            'feedback': feedback,
            'message': message,
            'attempts': session['attempts'],
            'game_over': session['game_over'],
            'guess': player_guess
        })
        
    except ValueError:
        return jsonify({'error': 'Oops! Please enter a valid number'})

@app.route('/new_game', methods=['POST'])
def new_game():
    """
    Starts a fresh game when the player wants to try again.
    Gives them a new problem and resets their tries.
    """
    # Create a new problem
    problem, answer = generate_equation()
    
    # Reset everything for the new game
    session['correct_answer'] = answer
    session['attempts'] = 0
    session['game_over'] = False
    session['equation_numbers'] = [int(n) for n in str(answer)]
    
    #Send the new problem to the player
    return jsonify({
        'equation': problem,
        'attempts': session['attempts'],
        'max_attempts': session['max_attempts']
    })

#Start the game when someone runs this file
if __name__ == '__main__':
    app.run(debug=True)
