FROM python:3.11-slim

WORKDIR /app

COPY persistent_auditor.py .

# Keep inventory.txt in /app/data so a volume can be mounted there,
# letting the file outlive the container.
RUN mkdir -p /app/data
ENV INVENTORY_FILE=/app/data/inventory.txt

CMD ["python", "persistent_auditor.py"]
