# textbase

Export an HTML file of your Instapaper articles, then using the URLs stored therein download the full text and store it - along with metadata - in a local SQLite database.

Originally conceived as an experiment with:
 * queue.Queue;
 * pathlib;
 * selenium;
 * beautifulsoup4;
 * newspaper3k;
 * generator expressions; 
 * SQLite; and
 * SQLAlchemy ORM,

written in a functional style. The intention is to reduce the number of external dependencies going forward.

## Configuration

* Currently only designed to work with Firefox as the Selenium back-end.  You'll need to have Firefox installed and the gecko webdriver (https://github.com/mozilla/geckodriver/releases) in your path.
* You will need to create 'config.yml' in the working directory from 'templates/config.yml', inserting your own Instapaper login and password.
* The codebase uses a custom logging library which is not public at this time - you will need to fork and setup your own logger, or else download without cloning and modify accordingly.

## Notes

* Git history prior to making this repo public has been deleted to prevent the unintentional disclosure of any sensitive information.
* TODOs remain in the code.
