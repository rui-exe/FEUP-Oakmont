# StockBroker-BDNR
Project in the scope of BDNR curricular unit @FEUP
## How to run the project
1. Clone the repository
2. Make sure to have installed the header files and static libraries for python dev for your version
of python. Then, install the required python packages with the following command:
```bash
pip install -r requirements.txt
```
3. Build the docker containers and run the project with the following command:
```bash
docker compose up --build
```
4. After the HBase Master server is functional and accepting connections, run the following python scripts:
```bash
python3 database_creation.py
python3 database_population.py
```