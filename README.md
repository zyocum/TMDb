# Query The Movie Database (TMDb) for actors who worked on the same movies/shows

## TMDb API
This script relies on the [TMDb API](https://www.themoviedb.org), so if you don't have an account with TMDb, you need to create one and [request an API key](https://www.themoviedb.org/settings/api).

## Usage

	./tmdb.py -h
	usage: tmdb.py [-h] [-k API_KEY] query [query ...]
	
	Search TMDb for common credits between cast/crew
	
	positional arguments:
	  query                 Names of persons to query
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -k API_KEY, --api-key API_KEY

**Note:** If you don't want to enter your API key every time, you can set a `TMDB_USER_KEY` environment variable and the script will use that instead:

	$ echo "export TMDB_USER_KEY=<your-key>" >> ~/.bash_profile
	$ . ~/.bash_profile

## Example

If you supply a single query you will get a complete credit list for that person:

	$ ./tmdb.py 'Nathan Fillion'
	{
	    "persons": [
	        "Nathan Fillion"
	    ],
	    "common_credits": [
	        "Being Canadian",
	        "Blast from the Past",
	        "Browncoats Unite: Firefly 10th Anniversary Special",
	        "Buffy the Vampire Slayer",
	        "Castle",
	        ...
	    ]
	}

If you supply multiple queries you will get credit results that all of those persons have in common:
	
	$ ./tmdb.py 'Nathan Fillion' 'Gina Torres'
	{
	    "persons": [
	        "Gina Torres",
	        "Nathan Fillion"
	    ],
	    "common_credits": [
	        "Browncoats Unite: Firefly 10th Anniversary Special",
	        "Castle",
	        "Con Man",
	        "Firefly",
	        "Justice League",
	        "Serenity"
	    ]
	}
