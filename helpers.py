# import dependencies
import csv
import math
import time
from config import proportion_to_rank_up, expected_headers, mastery_levels, all_ranks
from flask import render_template, request, session
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///flashcards.db")

def error(message,return_path):
  """Display error message simply"""
  return render_template("error.html",error=message,return_path=return_path)

def parse_csv(path):
  """Opening and parsing CSV into output word_dict"""

  #initialise variables
  word_dict = {"words": {}, "ranks": {}}
  headers_list = None

  # open csv and put all the words in the words dict
  with open(path, 'r') as words_csv:

    # go through each line in reader
    for line in csv.reader(words_csv):

      # if it's the first line (and so our headers are unknown)
      if not headers_list:

        # get the headers
        headers_list = line

        # validate headers in CSV
        if headers_list != expected_headers:
          return False

      # all other lines
      else:



        # add the word to the words dict
        curr_word = line[0]
        curr_answer = line[1]
        curr_rank = line[2]

        word_dict["words"][curr_word] = {"answer": curr_answer,
                                         "rank": curr_rank}

                # validate ranks
        if not line[2] in all_ranks:
          return False

        # if that rank doesn't exist, add it to ranks dict
        if not curr_rank in word_dict["ranks"]:
          word_dict["ranks"][curr_rank] = {'total_words': 1, 'words_req': 0}

        # otherwise increment the total number of words per rank in rank dict
        else:
          word_dict["ranks"][curr_rank]["total_words"] += 1

  # populating number of words required to master at each rank
  for rank in word_dict["ranks"]:

    # based on global var proportion_to_rank_up
    word_dict["ranks"][rank]["words_req"] = math.ceil(proportion_to_rank_up
                                             * word_dict["ranks"][rank]["total_words"])

  return word_dict

def update_words_per_user(updated_word, outcome, word_dict):
  """Given a word and how the user answered (correct or incorrect), update the database"""

  # get current unix timestamp
  current_time = int(time.time())

  # retrieve current stats for that word
  rows = db.execute("SELECT * FROM words_per_user WHERE user_id = ? AND word = ?", session["user_id"], updated_word)

  # check whether word is in the word list now, else exit function
  if not updated_word in word_dict["words"]:
    return "Word no longer in list - please contact your admin."

  # if user hasn't seen word, add it at lowest level and exit function
  if len(rows) != 1:
    db.execute("INSERT INTO words_per_user(user_id,word,rank,net_correct,level,last_answered) VALUES(?,?,?,?,?,?)",
               session["user_id"],
               updated_word,
               word_dict["words"][updated_word]["rank"],
               int(outcome),
               mastery_levels[0]["level"],
               current_time)

    return "New word added"

  current_word = rows[0]

  # save current level for that word
  current_level = current_word["level"]

  # save current net_correct for that word
  new_correct = current_word["net_correct"]

  # if user was correct: if within limits, increment net_correct
  if outcome:
    upper_limit = mastery_levels[len(mastery_levels)-1]["upper"]
    if new_correct < upper_limit:
      new_correct += 1

  # elif user was incorrect: if within limits, increment net_correct
  else:
    lower_limit = mastery_levels[0]["lower"]
    if new_correct > lower_limit:
      new_correct -= 1

  # regardless, get new level from net_correct
  # set default new level to the lowest in case outcome is somehow out of bounds
  new_level = mastery_levels[0]
  for level in mastery_levels:
    if new_correct <= level["upper"] and new_correct >= level["lower"]:
      new_level = level["level"]

  # set words_per_user net correct, new level, timestamp
  db.execute("UPDATE words_per_user SET level = ?, last_answered = ?, net_correct = ? WHERE user_id = ? AND word = ?",
             new_level,
             current_time,
             new_correct,
             session["user_id"],
             updated_word)

  # if new level is the highest level and old level wasn't:
  # update user stats
  if new_level == mastery_levels[len(mastery_levels)-1]["level"] and current_level != new_level:
    update_user_stats(word_dict)

  return "Word updated"

def update_user_stats(word_dict):
  """Updates the user's stats database on the basis of the words_per_user database.
  Called when a new word reaches the top mastery level, to see if the user has
  mastered enough words to rank up.
  The words mastered have to be from the currently existing word set (even if the user has
  previously learned other words)."""

  # if for some reason user doesn't have a set rank, initialise to 0

  # if for some reason user doesn't exist and no words found, return
  user_rows = db.execute("SELECT * FROM user_stats WHERE id = ?", session["user_id"])
  word_rows = db.execute("SELECT * FROM words_per_user WHERE user_id = ?", session["user_id"])

  if len(user_rows) == 0 and len(word_rows) == 0:
    return error("User not found - please contact your admin.", request.path)

  # default their new rank to 1, in case not enough words mastered
  new_rank = 1

  # get highest level possible (e.g. 'master')
  highest_level = mastery_levels[len(mastery_levels) - 1]["level"]

  # initialise the words_mastered for that user per rank
  words_mastered = {}
  for rank in all_ranks:
    words_mastered[rank] = 0

  # populate the words_mastered for that user per rank (if in word_dict)
  for word_row in word_rows:
    if word_row['level'] == highest_level and word_row["word"] in word_dict["words"]:
      words_mastered[word_row['rank']] += 1

  # in reverse order, compare words mastered against words required
  for mastered_rank in sorted(words_mastered.items(), reverse=True):

    # For this rank, how many words needed to progress to the next one up?
    req_for_current_rank = word_dict["ranks"][mastered_rank[0]]["words_req"]

    # If the user has mastered that many...
    if words_mastered[mastered_rank[0]] >= req_for_current_rank:

      # Find the next rank up - if it exists (else keep)
      current_rank_index = all_ranks.index(mastered_rank[0])
      if current_rank_index < len(all_ranks)-1:
        new_rank = all_ranks[current_rank_index+1]
      else:
        new_rank = mastered_rank[0]

      # once we've found the rank, stop the loop
      break

  # if for some reason user isn't in the table yet, add them; otherwise update their row
  if len(user_rows) == 0:
    db.execute("INSERT INTO user_stats(user_id,current_rank) VALUES(?,?)",
                   session["user_id"],
                   new_rank)
  else:
    db.execute("UPDATE user_stats SET current_rank = ? WHERE user_id = ?",
            new_rank,
            session["user_id"])



def get_available_words(word_dict):
  """Given current word_dict, checks list for words that are available in terms of rank and time last seen,
  based on user rank database and words per user database"""

  # gets user's current row
  user_rows = db.execute("SELECT * FROM user_stats WHERE user_id = ?", session["user_id"])

  # if user doesn't exist in that table for some reason, add them
  if len(user_rows) == 0:
    current_user_rank = all_ranks[0]
    db.execute("INSERT INTO user_stats(user_id,current_rank) VALUES(?,?)",
                   session["user_id"],
                   current_user_rank)
  else:
    # get user's current rank
    current_user_rank = user_rows[0]["current_rank"]

  # initialise empty words list
  available_words = []

  # go through words dict for current rank and below
  # get index of current rank in all_ranks list
  max_rank_index = all_ranks.index(current_user_rank)

  # get all words user has seen thus far
  seen_word_rows = db.execute("SELECT * FROM words_per_user WHERE user_id = ?", session["user_id"])

  # go through word_dict for that rank
  for possible_word, possible_details in word_dict["words"].items():

    # for each word:
    #if it's of an appropriate rank for the user
    if possible_details["rank"] <= current_user_rank:

      # get the row array for the word in question from the list of words the user has seen, if they've seen it
      current_rows = list(filter(lambda row: row['word'] == possible_word,
                          seen_word_rows))

      # if not there:
      if len(current_rows) > 1:
        return error("Error in word database - please contact your admin.", request.path)
      if len(current_rows) == 0:

        # add it to the available list
        available_words.append({'word': possible_word,
                                'answer': possible_details["answer"],
                                'last_answered': 0,
                                'time_now': int(time.time())
                                })

      # if it is there:
      else:
        current_row = current_rows[0]

        # check last seen time
        last_seen_time = current_row['last_answered']

        # check current level
        current_level = current_row['level']

        # check time needed for this level (from mastery_levels)
        time_needed = list(filter(
            lambda level_row: level_row['level'] == current_level,
            mastery_levels))[0]["seconds"]

        # check current time
        time_now = int(time.time())

        # check if enough time has passed
        if last_seen_time + time_needed <= time_now:

          # if so, add it to available list
          available_words.append({'word': possible_word,
                                  'answer': possible_details["answer"],
                                  'last_answered': last_seen_time,
                                  'time_now': time_now})

  return available_words