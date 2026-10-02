FROM python:3.11-slim

WORKDIR /app

COPY inventory_manager.py .

# Keep inventory.json in /app/data so a volume can be mounted there,
# letting the file outlive the container.
RUN mkdir -p /app/data
ENV INVENTORY_FILE=/app/data/inventory.json

CMD ["python", "inventory_manager.py"]
