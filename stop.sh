echo "Stopping all servers"
cd mlflow
./stop.sh
cd ..
cd dagster
./stop.sh
cd ..
cd elk
./stop.sh
echo "🛑 All servers stopped"