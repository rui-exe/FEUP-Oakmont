# StockBroker-BDNR
Project in the scope of BDNR curricular unit @FEUP
## How to run the project
1. Clone the repository
2. Make sure to have installed the header files and static libraries for python dev for your version
of python. Then, install the required python packages with the following command:

```bash
pip install -r requirements.txt
```

3. Create the .env file in the /backend and /hbase-client directories that are necessary to run the containers, for simplicity you can
simply copy the .example.env files.
```bash
cp backend/.example.env backend/.env
cp hbase-client/.example.env hbase-client/.env
```

4. Build the docker containers and run the project with the following command:

```bash
docker compose up --build
```

5. After the HBase Master server is functional and accepting connections, run the following python scripts:

```bash
python3 database_creation.py
python3 database_population.py
```
6. Optionally, you can run the following script in the background to perform real-time stock data updates:

```bash
python3 real_time.py
```
Just be sure to have your .env file configured with the correct IEX Cloud API key.