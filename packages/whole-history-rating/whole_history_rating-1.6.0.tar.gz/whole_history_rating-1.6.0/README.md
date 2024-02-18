
# Whole History Rating (WHR) Python Implementation

This Python library is a conversion from the original Ruby implementation of Rémi Coulom's Whole-History Rating (WHR) algorithm, designed to provide a dynamic rating system for games or matches where players' skills are continuously estimated over time.

The original Ruby code is available here at [goshrine](https://github.com/goshrine/whole_history_rating).

## Installation

To install the library, use the following command:

```shell
pip install whole-history-rating
```

## Usage

### Basic Setup

Start by importing the library and initializing the base WHR object:

```python
from whr import whole_history_rating

whr = whole_history_rating.Base()
```

### Creating Games

Add games to the system using `create_game()` method. It takes the names of the black and white players, the winner ('B' for black, 'W' for white), the day number, and an optional handicap (generally less than 500 elo).

```python
whr.create_game("shusaku", "shusai", "B", 1, 0)
whr.create_game("shusaku", "shusai", "W", 2, 0)
whr.create_game("shusaku", "shusai", "W", 3, 0)
```

### Iterating Towards Convergence

To refine the ratings towards stability, you can manually iterate:

```python
whr.iterate(50)
```

Or automatically iterate until the elo ratings stabilize:

```python
whr.auto_iterate(time_limit=10, precision=10E-3)
```

### Viewing Ratings

Retrieve and view player ratings, which include the day number, elo rating, and uncertainty:

```python
# Example output for whr.ratings_for_player("shusaku")
print(whr.ratings_for_player("shusaku"))
# Output:
#   [[1, -43, 0.84], 
#    [2, -45, 0.84], 
#    [3, -45, 0.84]]

# Example output for whr.ratings_for_player("shusai")
print(whr.ratings_for_player("shusai"))
# Output:
#   [[1, 43, 0.84], 
#    [2, 45, 0.84], 
#    [3, 45, 0.84]]

```

You can also view or retrieve all ratings in order:

```python
whr.print_ordered_ratings(current=False)  # Set `current=True` for the latest rankings only.
ratings = whr.get_ordered_ratings(current=False, compact=False)  # Set `compact=True` for a condensed list.
```

### Predicting Match Outcomes

Predict the outcome of future matches, including between non-existent players:

```python
# Example of predicting a future match outcome
probability = whr.probability_future_match("shusaku", "shusai", 0)
print(f"Win probability: shusaku: {probability[0]*100}%; shusai: {probability[1]*100}%")
# Output:
#   Win probability: shusaku: 37.24%; shusai: 62.76%  <== this is printed
#   (0.3724317501643667, 0.6275682498356332)
```

### Batch Loading Games

Load multiple games at once using a list of strings, with each string representing a game:

```python
whr.load_games(["shusaku shusai B 1 0", "shusaku shusai W 2", "shusaku shusai W 3 0"])
whr.load_games(["firstname1 name1, firstname2 name2, W, 1"], separator=",")
```

### Saving and Loading States

Save the current state to a file and reload it later to avoid recalculating:

```python
whr.save_base('path_to_save.whr')
whr2 = whole_history_rating.Base.load_base('path_to_save.whr')
```

## Optional Configuration

Adjust the `w2` parameter, which influences the variance of rating change over time, allowing for faster or slower progression. The default is set to 300, but Rémi Coulom used a value of 14 in his paper to achieve his results.

```python
whr = whole_history_rating.Base({'w2': 14})
```

Enable case-insensitive player names to treat "shusaku" and "ShUsAkU" as the same entity:

```python
whr = whole_history_rating.Base({'uncased': True})
```
