# Southwest Care Delivery Route Generator

## Prep
1. Clone the repo
    ```bash
    git clone https://github.com/3vanlock/sw_care_routes && cd sw_care_routes
    ```
2. Activate the virtual environment
    ```bash
    pipenv install
    ```
3. Set up your `secrets.py` file
    ```bash
    export API_KEY=<YourGoogleDeveloperAPI>
    echo GMAPS_API_KEY=$API_KEY > ./secrets.py
    ```

## Use
```bash
python app.py -h
```
```
usage: app.py [-h] [--origin ORIGIN] destinations

positional arguments:
  destinations     Pipe-separated list of destinations

optional arguments:
  -h, --help       show this help message and exit
  --origin ORIGIN
```

* Destination argument should be pipe-separated list
** "1001 Woodward Ave, Detroit, MI 48226, USA|2001 15th St, Detroit, MI 48216, USA|5458 Vernor Hwy, Detroit, MI 48209, USA"

```bash
python app.py "1001 Woodward Ave, Detroit, MI 48226, USA|2001 15th St, Detroit, MI 48216, USA|5458 Vernor Hwy, Detroit, MI 48209, USA"
['4322 W Vernor Hwy, Detroit, Michigan 48209', '5458 Vernor Hwy, Detroit, MI 48209, USA', '2001 15th St, Detroit, MI 48216, USA', '1001 Woodward Ave, Detroit, MI 48226, USA']
```
