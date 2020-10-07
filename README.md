# FastAPI_EuroConvension
This is a service whose task will be to convert to euro
the price we get. We build a REST API that receives prices, 
as well as the currency in which each of these prices is expressed, 
and will respond with these prices in euro (each request will consist of a single price).

In order to make the conversion from any currency to euro, we use exchangeratesapi.io

For performance reasons we build our API on top of FastAPI(which is fast and very high performance, on par with NodeJS and Go)
For caching mechanism we use Redis which has persistent volume.

# Required packages
Assuming that we have docker and docker-composed installed but if not please run the following commands:
- sudo apt  install docker.io python3-pip -y
- sudo -EH pip3 install docker-compose==1.24.1

# Deployment and run
(By default docker-compose group is not on sudo group so we need sudo access, otherwise we could simple run 'sudo usermod -aG docker $USER' to run docker-compose without sudo)
(Something like ansible seems overkill so we use the following setup)
- sudo docker-compose build && sudo docker-compose up

# Run test
(I build only one test which test a spesific day for a spesofic cuurency. We could add more days and currencies but seems overkill for now)
- pytest

You could test manual the app with curl enpoint as:
- curl -X POST "http://localhost:5000/currency/" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":100,\"currency\":\"USD\"}"
- curl -X POST "http://localhost:5000/currency/?historic_date=2015-2-2" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":0,\"currency\":\"string\",\"date\":\"string\"}"