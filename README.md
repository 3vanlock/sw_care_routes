# Southwest Care Delivery Route Generator

## TODO
* Read from CSV for simpler input
* Create x routes with y maximum stops
* Better handle mismatched address names

## Prep
1. Clone the repo
    ```bash
    git clone https://github.com/3vanlock/sw_care_routes && cd sw_care_routes
    ```
2. Activate the virtual environment
    ```bash
    pipenv install
    ```
3. Create and populate the `secrets.py` file in the project directory
    ```bash
    export API_KEY=<YourGoogleDeveloperAPI>
    echo GMAPS_API_KEY=$API_KEY > ./secrets.py
    ```
4. Create and populate the `destinations.csv` file in the project directory
  * Column order: `house_number,street,city,zip,name,phone`
  * Do not include the header column

## Use
```bash
python app.py -h
usage: app.py [-h] [--destinations-file DESTFILE] [--origin ORIGIN] drivers

positional arguments:
  drivers               Number of drivers to create routes for

optional arguments:
  -h, --help            show this help message and exit
  --destinations-file DESTFILE
                        File path of CSV file containing addresses and contact
                        info
  --origin ORIGIN
```
