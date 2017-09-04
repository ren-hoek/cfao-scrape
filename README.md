# cfao-scrape

Python module to scrape the result from enforcement searches made
 on the Chief Fire Officers Association website http://www.cfoa.org.uk

## Gettiing Started

### Installation
* Clone this repo
```
git clone https://github.com/ren-hoek/cfao-scrape.git
```
* Install [Anaconda Python](https://docs.continuum.io/anaconda/install)
* Create a conda environment for the scraper and pip install the python
 packages in [requirements.txt](./requirments.txt)
``` 
conda create --name cfao pip
source activate cfao
pip install -r requirements.txt
```
* [setup.sh](./setup.sh) will install and create the environment for Ubuntu/Mint distros 

### Files
* [cfao.py](./cfao.py): Module containing the functions required to perform and save the results
 as csv file 
* [scrape.py[](./scrape.py): Driver function for the scraping change the search parameters in the input
 section also the filename for the csv file is set in this section to

### Running
* Change the inputs for the search in [scrape.py[](./scrape.py)
* Run the scapper from the command line with the cfao environment activated
 (should see cfao in brackets at the start of the command line
```
python scrape.py
``` 

### Things to remember
* Running the scrape for all results will take around 3 hours
* Before running any scrape it is good to find out how many
 results it will generate
* If a scrape has a large number of result try to do it later in
 the evening to avoid putting undue strain on the website during
 the day 
