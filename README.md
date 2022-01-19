# CS50x Final Project: Dashcards
#### Video Demo:  https://www.youtube.com/watch?v=cXGvx8LKrEI
#### Description: A simple web app with login functionality which provides a spaced repetition flashcard system, with time in between repetitions increasing as mastery of one card increases, which will fully scale dynamically with any word list you input (provided it uses the same schema), meaning that you can use it for memorising anything, not just foreign language vocabulary!

## Helpers
First, let's look at the helper functions. These are all defined within *helpers.py*, and are just utility functions which save space in the main *app.py* program.
### error
Easy: renders the 'error.html' template with the error code provided, as well as providing a button back to the page which caused the error. It's honestly only very slightly more convenient than using *render_template* and inputting the values directly, but it's just quicker to type and a bit easier to read.
### parse_csv
Given the CSV address for the word list, parses into a dict of the following structure:
```
{
    'words': {
        '<WORD1>': {
            'answer': '<ANSWER1>',
            'rank': '<WORDRANK1>'
        },
        '<WORD2>': {
            'answer': '<ANSWER2>',
            'rank': '<WORDRANK2>'
        }
    },
    'ranks': {
        '<RANKNAME1>': {
            'total_words': <TOTAL_WORDS_IN_THIS_RANK>,
            'words_req': <WORDS_REQUIRED_FOR_RANK_UP>
        },
        '<RANKNAME2>': {
            'total_words': <TOTAL_WORDS_IN_THIS_RANK>,
            'words_req': <WORDS_REQUIRED_FOR_RANK_UP>
        }
    }
}
```
### update_words_per_user
Once the user answers a prompt, updates the *words_per_user* database entry for that word (or adds one, if it doesn't exist yet) - increasing 'net_correct' by 1 if the user got it right (assuming it's within bounds of the mastery levels - it won't go above 11 by default) or reducing it by 1 if the user got it wrong (similarly, won't go below 0). Also gets the current mastery level based on the new net_correct value and the bounds for each mastery level, defined in *mastery_levels* from *config.py*.
### update_user_stats
Called when a user reaches the maximum mastery level for a word, to see if the user should rank up (i.e. to see whether they've mastered the *proportion_to_rank_up* proportion of words at that rank, as from the *config* file). If so, updates the *user_stats* database entry for that user.
### get_available_words
Based on the user's current difficulty rank, and how long it's been since they last answered each word from that rank (since each word, depending on its mastery level, has a different amount of time that it makes you wait before it shows you again), generates a list of all the words that are eligible to be shown next: they have to be of the user's current rank or below, and the user has to have waited a minimum amount of seconds since the last time they answered it (based on the *seconds* variable in *mastery_levels* from *config.py*)
### db
This isn't a function but an object - the syntax for this largely was taken from CS50x's Unit 9 problem set, Finance; it was a very simple implementation of the concept and so didn't have much scope for change.

## App
Next we move onto the app itself, which handles displaying the pages to the user, as well as the final logic which needs to be calculated for each page itself (using the helper functions). Note that all templates draw from *layout.html* which, among other things, sets up a title, a navigation bar (including total number of words remaining as well as links to all other pages and a toggle for light/dark mode), and a container for the main content. The navigation bar also shows different available links if you are logged in or logged out.
### Index
The homepage has two different versions: one if you are logged in, and one if you are logged out. If logged out, it provides a message about why it's useful and why you should sign up, with two CTAs (one to register and one to log in). If logged in, it welcomes you back and reminds you that it's useful, with a CTA to start your session.
### Cards
Only available if logged in (else it redirects you back to the homepage). This page uses get_available_words to get all eligible words and then displays one of them at random. Once you answer one of the words, it will load the same page with a POST request instead, which will display (above the next new word) an alert letting you know whether you got the previous question right or wrong. If there are no available words remaining it will just give you a message letting you know that you've run out.
### Login
A simple login page, will return errors if the username and memorable phrase don't match any in the database, or if you leave either field empty.
### Logout
Not a page, but removes your 'user_id' field from the session cookie - and leaves your colour mode preference intact. Then redirects you to the logged-out homepage.
### Register
A simple registration page, will return errors if memorable phrases don't match, if the username is taken, or if any field is left empty. Auto logs the user in.
### Stats
Only available if logged in (else it redirects you back to the homepage). Displays three things: first, the difficulty rank which you, as a user, have achieved. Second, the number of words at each rank which you've reached each level of mastery at. And finally, a table of each individual word you've learned.
### Get JS data
This is to retrieve data from the frontend and store it in the session - namely, storing the user's dark mode/light mode preference, so that it persists between pages and even between visits.
### After request
Taken from the CS50 example from Week 9, to evoid caching of responses.

## Config
This file contains a number of global variables, used both by *app.py* and *helpers.py*, so is called by both.
### Word path
This only stores the path of where the wordlist CSV is stored.
### Proportion to rank up
This is an arbitrarily-decided fraction which indicates what proportion of the available words at a rank a user must master in order to achieve the next rank. Currently it is set at a default of 80%.
### Expected headers
Used when parsing the CSV - this ensures that the data is in the correct schema that we expect.
### Mastery levels
These are the levels of mastery at which you can have a word (currently beginner, intermediate, advanced and master, but the whole app will dynamically scale if you add more). It also includes, in the *lower* and *upper* attributes, the lower and upper bounds of the value of *net_correct* for this level of mastery - e.g. currently if you have the answer correct for one word 4 times, you have achieved 'intermediate'. And finally it includes the number of seconds that you have to wait between being shown that word, dependent on level of mastery - the better you know a word, the longer you wait between being shown it.
### All ranks
Just a list of all available word difficulty ranks in order. Not all ranks in this variable have to be present in the wordlist, but you cannot have a rank which appears in the wordlist and is missing from this variable.
## Flashcards Database
A sqlite3 database which stores information for each user.
### user_logins
Just assigns an id and stores the user's username and hashed memorable phrase, for login purposes. Each row should be unique per user and there should be no duplicates of *id* or *username*.
### user_stats
Per each user_id (the id assigned from the user_logins table), stores their current difficulty rank that they've achieved. Each row should be unique per user and there should be no duplicates of *user_id*.
### words_per_user
Stores a separate row for every word that every user has seen, with the user's ID, the word's difficulty rank, the user's current level of mastery of it, the number of net times the user has correctly answered it, and the time that it was last answered. Updated when the user answers a question.

## Static files
Next we move onto the static files, of which there are only a couple.
### Styles
This was the one that I found the most challenging since I only turned to it when I couldn't find a way to make Bootstrap do what I wanted - so most of it is slightly untidy attempts to overwrite Bootstrap's native CSS. I don't really have a justification for this one other than not understanding Bootstrap enough!

(One thing I will state, not specifically related to styles.css but more just to Bootstrap - I am very proud of how the website looks at any width, I managed to get familiar enough with Bootstrap to make it beautiful and responsive, and I think it looks great!)
### Colour Mode
This is a JS file which defines two functions: one whose function is only talking to the server to ask it to set the current colour mode (light mode vs dark mode) as a session variable so it's stored in the cookie. The other function toggles the current colour mode visually (as well as setting the window-level global variable which saves the current mode). It does this by iterating through an array (which was manually set up based on design decisions while going through each element) of objects, each containing: a selector, a class for light mode for all elements of that selector, and a class for dark mode for all elements of that selector. Just to ensure that we're only changing the elements we want to change, the elements with colour-related classes also all have a *.light-mode* or *.dark-mode* class, which this function targets too (so if you don't want something to change, don't set *.light-mode* or *.dark-mode* on it).

Based on the current mode (and therefore what the new mode will be), the function then iterates through each selector, gets all elements which have that selector + the mode class, and switches it to the appropriate new class based on mode. E.g. if the window is currently in light-mode, it will iterate through each object and add *.light-mode* to the value from the *selector* attribute. Then, for every element selected by this new selector, if it has the class which is described by the current object's *light-mode* attribute, it removes it and adds the class described by the current object's *dark-mode* attribute.

## Design Decisions
This section will describe the various non-code-specific design decisions that I've made, some of which will have been partially covered when talking about the code, but that I want to describe outside of the context of code at all.
### Difficulty Ranks
The terminology 'rank' applies at two different levels: at the word level, and at the user level (although it refers to the same rank in both instances).

Essentially the intention is that I wanted to have a mechanism by which you can progress from easier words to harder words, inspired by some of my previously-used language learning spaced-repetition platforms such as WaniKani. This means that one of the three required fields in the wordlist CSV (the other two being the word itself and its meaning) is that word's current difficulty rank. Then the user themselves has a difficulty rank which they've attained, and they won't ever be shown any words that are harder than their user rank. E.g. if a user has reached difficulty rank 3, they'll be shown words of rank 1-3, but never 4.

By default, for ease, I've just given the ranks numerical names, although formatted as strings always, but these could really be named anything.

That said, the way the code is currently written (because of one line in *update_user_stats* which sorts them in reverse order), it requires them to be in alphanumeric order based on ascending difficulty. This isn't a problem for me because, as mentioned, they're currently just numbers, but I can think of a couple tidiers way to do this if I did want it to be more flexible to different rank names. (I can't just reverse the list itself without sorting, because I don't actually sort the list, I just sort the ranks from another object)

One tidy option is, instead of just a list of strings, it could be a list of objects similar to mastery_levels, with one attribute associated with the ascending difficulty order and the other describing the name. I can then use that whenever I iterate through it.

Alternatively I could approach it differently: I could store the user's rank as just a numerical index, and then have a list which displays all the names of ranks in ascending difficulty order. Then the index could be used to look up the name in the list, and when I reverse the order in *update_user_stats* I could just reverse the list of indices, keeping the list of names the same.

There's a slight question here as to whether this could lead to mismatch between index and name. E.g. if, partway through the site's lifetime, I added a new rank in between 3 and 4 (called 3.5), what would I want users at rank 4 to do? Have they rightfully achieved "rank 4" and get to keep it, or have they really only reached the 4th overall rank, which is now 3.5? Well, probably the answer depends on what words are introduced: whether the words previously described as rank 4 will also move, or if they shift down.

A lot of the decisions that I made when designing this website were based on the idea of it being dynamic based on input - which I do still stand by, because it's good programming practice and it just makes reasonable sense, and it saves me time as well if I do decide to change something (given that the site isn't really live to users). But after a certain point, if I'm thinking about this as if it's a real website, I'd have to think about what things would feel reasonable to change while users are using it and have stats etc built up, and what things it doesn't make sense to change unless really necessary; I'd have to think about impact on users of various changes; etc. So while it's possible to add a new rank in the middle, and theoretically the program would be fine, if it was a live site for users I'd have to really be able to justify the impact of the decision before doing it.
### Mastery Levels
This was introduced as a way of bucketing how well the user's learned a word. This is for two main functions (well, and a third auxiliary one): one is to be able to determine what difficulty rank the user has attained, which I'll explain in a separate subsection, and the other is to determine how long to wait after each instance of being shown a word. The better a user knows a word, the less frequently they need to be shown it, since it's been consolidated into their memory better already. The third auxiliary one is that then the user gets to have a visual output of their progress in the Stats page, which is always encouraging for learners!

This is also inspired by similar spaced-repetition systems that I love, like WaniKani (although that particular platform uses Apprentice, Guru, Master, Enlightened, and Burned - but the idea is similar).
### Ranking Up
The final piece of the rank-level puzzle, which requires context of both difficulty ranks and mastery levels, is the process by which a user levels up. This is briefly described in my explanation of *update_user_stats* since that's the purpose of that function, but to explain it outside of the context of code:

The criteria for ranking up is currently that you have at least a certain proportion of words at your current rank, learned at the highest available mastery level. Currently this is set by default to 80% (in the *proportion_to_rank_up* variable from *config.py*, as described above) but this can be changed by just altering that variable. When determining if a user should rank up, we: get the total number of words in the current rank in the word list; multiply it by the proportion (and round up) to get the minimum required words to reach the next rank; check how many words **from the word list** the user has learned at that rank and if it reaches the minimum, then congratulations, they get to rank up.

While this description is broadly code-agnostic, the above logic means that we only have to check whether the user has ranked up if they've just mastered another word (to the highest mastery level), e.g. them going Beginner->Advanced won't ever trigger a rank up. That means that we only call *update_user_stats* once a user reaches max level on a new word (which then checks the criteria).
## Future iterations
Going through this project while it's more or less finished has uncovered a number of things that I would probably have changed, if I were to put in approximately the same amount of time again to build a new-and-improved Version 2. I didn't have most of these planned to start with because I didn't think of them, so I'm still happy to call Version 1 a completed project; but largely the reason I didn't end up doing any of the below changes is because the scale of the project was already fairly substantial and I think it would really have to be a whole extra phase of work. But, one day:
### Store last edited time of word list
Currently I call *parse_csv* for every single page - this is in my attempts to make sure it's dynamic and the user doesn't have a confusing mismatched experience if someone in the backend changes the wordlist partway through a user's session. This works alright now, but I'm aware it won't scale well if the wordlist becomes enormous.

One potential way to solve this: check when the wordlist csv was **last updated**, and use that to determine whether we should re-parse the CSV (e.g. perhaps storing in a database at the user level the last time we updated the word list for them specifically, and then comparing that to the time the CSV was last updated, and then re-parsing if it's out of date).
### Allow two-way learning
At the moment, I'm only allowing users to learn their flashcards in one direction (given the word, provide its meaning), when in reality, for a lot of things especially like language vocabulary learning, it's really much more useful to be able to do this recall in both  directions (e.g. also, given a meaning, provide the word). This one I did actually consider from the beginning whether I should implement, but I think it belongs in a Version 2.

The main complexities to consider are: do I want people to be able to toggle on/off whether they're being given the cards in reverse? For mastery, would a user have to be able to do both versions of both sides? Would we want to try to somehow upweight the probability a user sees the other side of a card after they've seen the first side? (e.g. if they only do a couple of words per session, currently if the way to display a word is random, they could end up see the 'word' part of it multiple times before ever seeing the 'answer' part). Or would it be more like a toggle at word level - the last time you saw this word you saw the 'word', so now we'll show you the 'answer' (although then, what do you do if they got one wrong - repeat that one or flip it again?)

It's not insurmountable, but many things to consider!
### Provide other functionality for user login e.g. change/reset password, email confirmation, etc;
This is just useful for user experience and it's what they're used to on other sites. Currently if a user forgets their password, we don't have their email address so we have no way to verify their identity, so they're locked out. A way of setting up an email confirmation (to make sure it's really their email) and then providing a password reset option sent to them via email would really go a long way to making it feel like a "real" website, but I think would be quite complex. Even easier than that, though, just being able to change your password if you know your current one would be a big step.
### Hash password before sending
It's currently not at all secure - the password (or as I've insisted on calling it, "memorable phrase", so that nobody actually puts a real password in, obviously!) is sent to the server in plaintext for potentially anybody to intercept. Some way of being able to hash it before the request is sent would make it much more secure and I'd be much happier asking people for a password.
### Allow close matches/slight misspellings
Again, inspired by other flashcard-type sites I've used... allowing for typoes and slight misspellings (with a little message to alert you, but accepting it as correct anyway). I'm not really sure how I'd go about doing this - I'm assuming not manually (?) but I don't know if I'd have to come up with some sort of algorithm or if there's a pre-packaged way to go about doing this. Would have to do some research!
### List out all future words
Another one inspired by other sites, maybe as well as having the user see which words they know how well, maybe letting them see a list of upcoming words so they know what to look forward to? This one isn't a definite, but could be interesting.
### Stop displaying mastered words (or add final level of mastery which isn't necessary to reach)
This is a tricky one. Currently you have to have reached the final level of mastery in a number of words to rank up, and at that level of mastery I've added a significant period of time you have to wait until seeing that word again (a day). But there's probably a point at which you really want to stop seeing that word barely at all, maybe more like once per week - so maybe I should add a new rank above master (perfected?), but change the code so 'master' is still the benchmark for ranking up? Or I could just massively scale up the time in between each word being displayed at each level, but I don't want users to get bored and stop visiting because they never have any words available!
### Generate new user_ids
At the moment, the user's user_id is generated based on their auto-generated numerical *id* field in *user_logins* (which is just incremented by 1 for every new row). This generally works fine... but if you delete the last row in *user_logins* for whatever reason, then add a new row in, the new row will have the same *id* as the last one, meaning that all this old user's data would be associated with the new user. Obviously it's unlikely we'd ever delete a row from one table and not the others, but still, it opens up a strange vulnerability. Better to generate a random string or random series of numbers, I think, and use that as the common ID.
### Work on better CSS styling/integration with Bootstrap
Would be better if most of the lines in my *styles.css* didn't include the *important!* flag - perhaps looking further into working with Bootstrap or customising it in a more stable way.
### Allow user-generated wordlists
I'm on the fence about this one, but my design philosophy for this site has always been that it can dynamically adapt to new word lists, and that spaced repetition isn't just for language learning. I think I want more wordlists to be available to the user than just my pre-set one (because I'm learning one particular language, but users might want to learn another). But I'm not sure if I want it to be more Duolingo-esque (select a language and learn some pre-set vocab based on that language; less flexible, but much less work required by the user) or more Anki-esque (much more customisable/flexible, use it for any language or even other types of memorisation, but requires a fair amount of work upfront).

If the former, maybe I could come up with some different wordlists and have the user choose which one they want to use? (And again like Duolingo - maybe even have them switch into different language 'modes' if they want to use more than one - with separate stats etc in each language?)

If the latter, maybe I could allow the user to upload their own CSVs? Then again, I'd have to decide whether to force them to only be able to use one CSV, so uploading a new one will overwrite the old one; or, whether to let them have multiple (if I do really want it to be flexible), but then I run into the same issue with the Duolingo-style version, where I'd need to store stats for each one separately - and dynamically! - perhaps with a distinct ID per word set? In any case it'd definitely require a substantial database restructure!

One other major consideration with uploading your own wordlists is that they need a place to be stored! If I'm imagining this were a "real" site, this definitely couldn't be something that I did in its current iteration because the server where I'd be hosting it has a fixed file size, and I would want it to be scalable - probably by using some kind of cloud service (Google Cloud Platform, Microsoft Azure, Amazon Web Services, etc) so that it can scale depending on the amount of storage needed. Something that's not currently financially viable for me to pursue but, if it was actually used by a lot of people, might be something to explore!

The third option for flexibility in word lists I think would be a hybrid of the two - having a few presets written by me, and then also being able to upload user-generated lists. Maybe even having a gallery, where if users set their lists to public, other users could download them...? The possibilities are endless!

# Thank you
Thank you for reading all of this! This has been one of the most fulfilling projects I've been able to complete to date, and it was such a great mix of feeling like I was driving it completely on my own, while also being inspired by (but not mimicking) existing platforms that I like, and also while using and benefitting from some preset code (e.g. Bootstrap and its default templates) while also completely customising it and making it my own.

I'm very proud of Dashcards and I can't wait for my next project!