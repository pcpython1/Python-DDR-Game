import time
import pyttsx3
import random
import threading
import keyboard
import pymongo
import os
from playsound import playsound

# initialize DB
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# db name
user_db = myclient["ddr"]
# column we are using for our schema
users_col = user_db['users']

##### global funcs ######

def speak(msg):
    start_voice = pyttsx3.init()
    start_voice.setProperty('volume', 2.0)
    rate = start_voice.getProperty('rate')
    start_voice.setProperty('rate', rate-20)
    start_voice.say(msg)
    start_voice.runAndWait()

def get_users():
    users = []
    print('Please type 1 or 2 depending on the number of players.')
    speak('Please type 1 or 2 depending on the number of players.')
    players = int(input('Number of Players: '))
    if players == 1:
        print('Please type your username.')
        speak('Please type your username.')
        username = str(input("Username: "))
        time.sleep(1)
        print(f'Hello {username}.')
        speak(f'Hello {username}.')
        users.append(User(username))
    else:
        print('Player 1 please type your username.')
        speak('Player 1 please type your username.')
        username1 = str(input("User 1: "))
        time.sleep(1)
        print('Player 2 please type your username.')
        speak('Player 2 please type your username.')
        username2 = str(input("User 2: "))
        time.sleep(1)
        print(f'Hello {username1} and {username2}.')
        speak(f'Hello {username1} and {username2}.')
        users.append(User(username1))
        users.append(User(username2))

    return users

def get_difficulty():
    print('Select a difficulty using 1, 2, or 3. 1 is easy, 2 is medium, and 3 is hard.')
    speak('Select a difficulty using 1, 2, or 3. 1 is easy, 2 is medium, and 3 is hard.')
    difficulty = int(input('Difficulty: '))
    time.sleep(2.5)

    return Difficulty(difficulty-1)

def get_song():
    print('Currently supported songs:')
    speak('Currently supported songs:')
    print('1: Glock+onion by Aphex Twin')
    speak('1: Glock+onion by Aphex Twin')
    print('2: Crab Rave by Noisestorm')
    speak('2: Crab Rave by Noisestorm')
    print('3: Cotton Eye Joe by Rednex')
    speak('3: Cotton Eye Joe by Rednex')
    inp = int(input('Song: '))
    if inp == 1:
        song = 'afx.mp3'
        speak('You chose glock+onion by Aphex Twin.')
    if inp == 2:
        song = 'Crab Rave.mp3'
        speak('You chose Crab Rave by Noisestorm.')

    if inp == 3:
        song = 'Cotton Eye Joe.mp3'
        speak('You chose Cotton Eye Joe by Rednex.')

    return song

##########################

class User:
    username = ''
    achievements = []
    points = 0

    def __init__(self, username):
        self.username = username.strip()
        self.check_if_user_exists()
        self.check_achievement_requirements()

    def check_if_user_exists(self):
        x = users_col.find_one({'username':self.username})
        if x:
            self.points = x['points']
            self.achievements = x['achievements']

        if not x:
            if len(self.username) > 0:
                self.add_user_to_database()
            else:
                raise Exception("Username must be at least 1 letter long")

    def add_user_to_database(self):
        users_col.insert_one({"username":self.username, "achievements":[], "points":0})

    def add_points_to_database(self, points):
        users_col.update_one({"username":self.username}, {"$set":{"points":(self.points + points)}})

    def add_achievements_to_database(self):
        users_col.update_one({"username":self.username}, {"$set":{"achievements":self.achievements}})

    def check_achievement_requirements(self):
        if self.points >= 100:
            achievement = 'Beginner: Accrue 100 points.'
            if achievement not in self.achievements:
                print(f'{self.username} unlocked new achievement: {achievement}')
                speak(f'{self.username} unlocked new achievement: {achievement}')
                self.achievements.append(achievement)

        if self.points >= 250:
            achievement = 'Amateur: Accrue 250 points.'
            if achievement not in self.achievements:
                print(f'{self.username} unlocked new achievement: {achievement}')
                speak(f'{self.username} unlocked new achievement: {achievement}')
                self.achievements.append(achievement)

        if self.points >= 1000:
            achievement = 'Expert: Accrue 1000 points.'
            if achievement not in self.achievements:
                print(f'{self.username} unlocked new achievement: {achievement}')
                speak(f'{self.username} unlocked new achievement: {achievement}')
                self.achievements.append(achievement)

        if self.points >= 2500:
            achievement = 'Pro: Accrue 2500 points.'
            if achievement not in self.achievements:
                print(f'{self.username} unlocked new achievement: {achievement}')
                speak(f'{self.username} unlocked new achievement: {achievement}')
                self.achievements.append(achievement)

        self.add_achievements_to_database()

    def speak_user(self):
        if len(self.achievements) > 0:
            print(f'User {self.username} has accrued {self.points} points, and has unlocked the following achievements:')
            speak(f'User {self.username} has accrued {self.points} points, and has unlocked the following achievements:')
            print(f'{self.achievements}')
            speak(f'{self.achievements}')
        else:
            print(f'User {self.username} has accrued {self.points} points, and has unlocked no achievements.')
            speak(f'User {self.username} has accrued {self.points} points, and has unlocked no achievements.')

class Difficulty:
    difficulty_level = 0
    key_press_delay = 0.0

    def __init__(self, difficulty_level):
        self.difficulty_level = difficulty_level
        self.key_press_delay = self.calculate_delay(difficulty_level)

    def calculate_delay(self, difficulty_level):
        if difficulty_level == 0:
            return 1.0

        if difficulty_level == 1:
            return .75

        if difficulty_level == 2:
            return .5

        else:
            raise Exception('Invalid difficulty level.')

class Song:
    # two variables just in case its multiplayer
    # points2 = second player pts
    points = 0
    points2 = 0

    def __init__(self, song_file, difficulty):
        self.song_file = song_file
        self.difficulty = difficulty
        self.delay = difficulty.key_press_delay

    # have to use another speak method because the threading doesnt
    # allow global speak threads.. idk its a weird bug
    def speak(self, msg):
        try:
            song_voice = pyttsx3.init()
            song_voice.setProperty('volume', 4.0)
            rate = song_voice.getProperty('rate')
            song_voice.setProperty('rate', rate-30)
            song_voice.say(msg)
            song_voice.runAndWait()
        except:
            pass

    def start_song(self):
        # start playing it
        playsound(self.song_file, block=False)

    def get_song_length(self):
        if self.song_file == "afx.mp3":
            length = 207

        if self.song_file == "Crab Rave.mp3":
            length = 168

        if self.song_file == "Cotton Eye Joe.mp3":
            length = 195

        return int(length*.5)

    def wait_for_input(self, key):
        p1_keys = ['up', 'left', 'right', 'down']
        p2_keys = ['w', 'a', 's', 'd']

        try:
            now = time.time()
            key_pressed = keyboard.read_key()
            after = time.time()
            # delay * 1.25 to account for human delay
            if after-now <= (self.delay*1.25):
                if key_pressed == key:
                    if key in p1_keys:
                        self.points += 1
                        print(f'{key} - +1')

                    if key in p2_keys:
                        self.points2 += 1
                        print(f'{key} - +1')

                else:
                    print(f'{key} - +0')

        except Exception as e:
            pass

    def begin_solo(self):
        # start song
        song_playing = threading.Thread(target=self.start_song)
        song_playing.start()

        # placeholder var so you don't get
        # same input twice in a row
        last_press = 999

        # let the song begin
        time.sleep(10)

        # calculate length of song
        for i in range(self.get_song_length()):
            r = random.randint(0, 3)

            # makes sure the same key isn't given twice
            while r == last_press:
                r = random.randint(0, 3)

            if r == 0:
                speak_up = threading.Thread(target=self.speak, args=('up',))
                wait_up = threading.Thread(target=self.wait_for_input, args=('up',))
                speak_up.start()
                wait_up.start()
                time.sleep(.66)

            if r == 1:
                speak_left = threading.Thread(target=self.speak, args=('left',))
                wait_left = threading.Thread(target=self.wait_for_input, args=('left',))
                speak_left.start()
                wait_left.start()
                time.sleep(.66)

            if r == 2:
                speak_right = threading.Thread(target=self.speak, args=('right',))
                wait_right = threading.Thread(target=self.wait_for_input, args=('right',))
                speak_right.start()
                wait_right.start()
                time.sleep(.66)

            if r == 3:
                speak_down = threading.Thread(target=self.speak, args=('down',))
                wait_down = threading.Thread(target=self.wait_for_input, args=('down',))
                speak_down.start()
                wait_down.start()
                time.sleep(.66)

            last_press = r
            time.sleep(1)

        print(f'Final Score: {self.points}')

    def begin_mp(self):
        # start song
        threading.Thread(target=self.start_song).start()

        # placeholder var so you don't get
        # same input twice in a row
        last_press = 999

        # let the song begin
        time.sleep(10)

        # calculate length of song
        for i in range(self.get_song_length()):
            r = random.randint(0, 3)

            # makes sure the same key isn't given twice
            while r == last_press:
                r = random.randint(0, 3)

            if r == 0:
                speak_up = threading.Thread(target=self.speak, args=('up',))
                wait_up = threading.Thread(target=self.wait_for_input, args=('up',))
                wait_up2 = threading.Thread(target=self.wait_for_input, args=('w',))
                speak_up.start()
                wait_up.start()
                wait_up2.start()
                time.sleep(.6)

            if r == 1:
                speak_left = threading.Thread(target=self.speak, args=('left',))
                wait_left = threading.Thread(target=self.wait_for_input, args=('left',))
                wait_left2 = threading.Thread(target=self.wait_for_input, args=('a',))
                speak_left.start()
                wait_left.start()
                wait_left2.start()
                time.sleep(.6)

            if r == 2:
                speak_right = threading.Thread(target=self.speak, args=('right',))
                wait_right = threading.Thread(target=self.wait_for_input, args=('right',))
                wait_right2 = threading.Thread(target=self.wait_for_input, args=('d',))
                speak_right.start()
                wait_right.start()
                wait_right2.start()
                time.sleep(.6)

            if r == 3:
                speak_down = threading.Thread(target=self.speak, args=('down',))
                wait_down = threading.Thread(target=self.wait_for_input, args=('down',))
                wait_down2 = threading.Thread(target=self.wait_for_input, args=('s',))
                speak_down.start()
                wait_down.start()
                wait_down2.start()
                time.sleep(.6)

            last_press = r
            time.sleep(1)

        print(f'Player 1 score: {self.points}\nPlayer 2 score: {self.points2}')

    def get_p1_points(self):
        return self.points

    def get_p2_points(self):
        return self.points2

class Game:
    multiplayer = False
    score = 0
    score2 = 0

    def __init__(self, song, difficulty, users):
        self.song = song
        self.difficulty = difficulty
        self.users = users
        if len(users) == 2:
            self.multiplayer = True

    def start_game(self):
        Playing = True
        print('Game is starting, get ready!')
        speak('Game is starting, get ready!')
        if self.multiplayer:
            speak('To score points, player 1 uses the arrow keys and player 2 uses W, A, S, and D. You both fight over the same point. Good luck!')
            start_song = threading.Thread(target=self.song.begin_mp)
        elif not self.multiplayer:
            speak('Use the arrow keys to score points. Good luck!')
            start_song = threading.Thread(target=self.song.begin_solo)

        start_song.start()

        while Playing == True:
            if not start_song.is_alive():
                self.score = self.song.get_p1_points()
                self.score2 = self.song.get_p2_points()

                break

            time.sleep(5)

        self.finish_game()

    def finish_game(self):
        time.sleep(5)
        if self.multiplayer:
            speak(f'{self.users[0].username} scored {self.score} that play, and {self.users[1].username} scored {self.score2}. Good job!')
            users[0].add_points_to_database(self.score)
            users[1].add_points_to_database(self.score2)

        else:
            speak(f'{self.users[0].username} scored {self.score} that play. Good job!')
            users[0].add_points_to_database(self.score)

class Leaderboard:
    scores = []
    def __init__(self):
        self.scores = []
        self.get_scores_from_database()

    def get_scores_from_database(self):
        for x in users_col.find():
            if x['points'] not in self.scores:
                self.scores.append(x['points'])

    def display_leaderboard(self):
        if len(self.scores) > 0:
            old_scores = self.scores
            self.scores = sorted(old_scores, reverse=True)
            counter = 1
            for i in range(len(self.scores)):
                for u in users_col.find({'points':self.scores[i]}):
                    sentence = f"#{counter}: {u['username']} with {self.scores[i]} points"
                    print(sentence)
                    speak(sentence)
                    counter += 1

            print('\n')
        else:
            print('No scores exist in your database.')
            speak('No scores exist in your database.')

##########################

# this is like saying int main() in c++
if __name__ == "__main__":
    choice = 0
    print('Welcome to Dance Dance Revolution for the blind. This game will give you a choice of songs to play along with audio cues to know when to press the arrow keys.')
    speak('Welcome to Dance Dance Revolution for the blind. This game will give you a choice of songs to play along with audio cues to know when to press the arrow keys.')
    while (choice != 4):
        print('Please choose what you would like to do in accordance with these numbers:')
        speak('Please choose what you would like to do in accordance with these numbers:')
        print('1: Play Dance Dance Revolution')
        speak('1: Play Dance Dance Revolution')
        print('2: Check the Leaderboard')
        speak('2: Check the Leaderboard')
        print('3: Check User\'s Stats')
        speak('3: Check User\'s Stats')
        print('4: Quit\n')
        speak('4: Quit')
        choice = int(input('Choice: '))
        if choice == 1:
            users = get_users()
            for user in users:
                user.speak_user()

            difficulty = get_difficulty()
            song_name = get_song()
            song = Song(song_name, difficulty)
            Game = Game(song, difficulty, users)
            Game.start_game()

        if choice == 2:
            leaderboard = Leaderboard()
            leaderboard.display_leaderboard()

        if choice == 3:
            speak('Please type the name of the user who you would like to look up.')
            n = str(input("User to look up: "))
            checking = User(n)
            checking.speak_user()
